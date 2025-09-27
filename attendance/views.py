# attendance/views.py
import cv2
import numpy as np
import face_recognition
import json
from datetime import date, datetime
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.core.management import call_command
from django.db import transaction
from .models import Student, Attendance, AttendanceSession
import threading
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionCamera:
    def __init__(self):
        self.camera = None
        self.is_active = False
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roll_nos = []
        self.known_student_ids = []
        self.attendance_marked = set()
        self.frame_count = 0
        self.recognition_threshold = 0.5
        self.current_session = None

        # Load face encodings
        self.load_face_encodings()

    def load_face_encodings(self):
        """Load face encodings from database"""
        try:
            students = Student.objects.filter(face_encoding__isnull=False)

            self.known_face_encodings = []
            self.known_face_names = []
            self.known_face_roll_nos = []
            self.known_student_ids = []

            for student in students:
                if student.face_encoding and len(student.face_encoding) == 128:
                    self.known_face_encodings.append(
                        np.array(student.face_encoding))
                    self.known_face_names.append(student.name)
                    self.known_face_roll_nos.append(student.roll_no)
                    self.known_student_ids.append(student.id)

            logger.info(
                f"Loaded {len(self.known_face_encodings)} face encodings")
            return True

        except Exception as e:
            logger.error(f"Error loading face encodings: {e}")
            return False

    def start_camera(self, user=None):
        """Start camera and create session"""
        try:
            if self.camera is not None:
                self.stop_camera()

            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                logger.error("Could not open camera")
                return False

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            self.is_active = True
            self.attendance_marked.clear()
            self.frame_count = 0

            # Create attendance session
            if user:
                self.current_session = AttendanceSession.objects.create(
                    name=f"Face Recognition - {datetime.now().strftime('%H:%M')}",
                    created_by=user,
                    is_active=True
                )

            logger.info("Camera started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        """Stop camera and end session"""
        try:
            self.is_active = False

            if self.camera is not None:
                self.camera.release()
                self.camera = None

            # End current session
            if self.current_session:
                self.current_session.total_recognized = len(
                    self.attendance_marked)
                self.current_session.end_session()
                self.current_session = None

            cv2.destroyAllWindows()
            logger.info("Camera stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Error stopping camera: {e}")
            return False

    def generate_frames(self):
        """Generate camera frames with face recognition"""
        while self.is_active and self.camera is not None:
            try:
                success, frame = self.camera.read()
                if not success:
                    break

                self.frame_count += 1

                # Process every 3rd frame for performance
                if self.frame_count % 3 == 0:
                    frame = self.process_frame(frame)

                # Encode frame as JPEG
                ret, buffer = cv2.imencode(
                    '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                logger.error(f"Error generating frame: {e}")
                break

    def process_frame(self, frame):
        """Process frame for face recognition"""
        try:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find faces in current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)

            # Process each face
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back coordinates
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=self.recognition_threshold
                )

                name = "Unknown"
                confidence = 0
                student_id = None

                if matches and any(matches):
                    # Find best match
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, face_encoding
                    )
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        student_id = self.known_student_ids[best_match_index]

                        # Mark attendance if not already marked
                        if student_id not in self.attendance_marked and confidence > 0.4:
                            self.mark_attendance(student_id, confidence)
                            self.attendance_marked.add(student_id)

                # Draw rectangle and label
                color = (0, 255, 0) if student_id else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                # Draw label
                label = f"{name} ({confidence:.2f})" if confidence > 0 else name
                cv2.rectangle(frame, (left, bottom - 35),
                              (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            # Add status overlay
            self.add_status_overlay(frame)

            return frame

        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame

    def add_status_overlay(self, frame):
        """Add status information to frame"""
        try:
            height, width = frame.shape[:2]

            # Status background
            cv2.rectangle(frame, (10, 10), (300, 100), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, 10), (300, 100), (255, 255, 255), 2)

            # Status text
            cv2.putText(frame, f"Students: {len(self.known_face_encodings)}",
                        (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Present: {len(self.attendance_marked)}",
                        (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {self.frame_count}",
                        (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        except Exception as e:
            logger.error(f"Error adding overlay: {e}")

    def mark_attendance(self, student_id, confidence):
        """Mark attendance for recognized student"""
        try:
            student = Student.objects.get(id=student_id)
            attendance, created = Attendance.mark_attendance(
                student=student,
                status='present',
                confidence=confidence,
                notes=f'Face recognition - {confidence:.2f} confidence'
            )

            if created:
                logger.info(
                    f"Marked attendance for {student.name} ({confidence:.2f})")
            else:
                logger.info(
                    f"Updated attendance for {student.name} ({confidence:.2f})")

        except Exception as e:
            logger.error(f"Error marking attendance: {e}")


# Global camera instance
camera = FaceRecognitionCamera()


@login_required
def take_attendance(request):
    """Main attendance taking page"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(
            request, 'You do not have permission to take attendance.')
        return redirect('student_dashboard')

    context = {
        'today_date': date.today(),
        'total_students': Student.objects.count(),
        'students_with_encodings': Student.objects.filter(face_encoding__isnull=False).count(),
    }
    return render(request, 'attendance/take_attendance.html', context)


def video_feed(request):
    """Video streaming endpoint"""
    try:
        if not camera.is_active:
            # Start camera if not active
            if not camera.start_camera(request.user if request.user.is_authenticated else None):
                return HttpResponse("Camera not available", status=503)

        return StreamingHttpResponse(
            camera.generate_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"Video feed error: {e}")
        return HttpResponse("Video feed error", status=500)


@login_required
@require_http_methods(["POST"])
def stop_camera(request):
    """Stop camera endpoint"""
    try:
        success = camera.stop_camera()
        return JsonResponse({
            'success': success,
            'message': 'Camera stopped successfully' if success else 'Error stopping camera',
            'recognized_count': len(camera.attendance_marked)
        })
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def attendance_status(request):
    """Get current attendance status"""
    try:
        total_students = Student.objects.count()
        today_attendance = Attendance.objects.filter(date=date.today())
        present_count = today_attendance.filter(status='present').count()

        # Get recognized students in current session
        recognized_students = []
        if camera.attendance_marked:
            recognized_students = list(Student.objects.filter(
                id__in=camera.attendance_marked
            ).values('id', 'name', 'roll_no'))

        return JsonResponse({
            'success': True,
            'total_students': total_students,
            'present_count': present_count,
            'recognition_active': camera.is_active,
            'session_recognized': len(camera.attendance_marked),
            'recognized_students': recognized_students,
        })

    except Exception as e:
        logger.error(f"Error getting attendance status: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def students_api(request):
    """Get students list for attendance"""
    try:
        students = Student.objects.all().values(
            'id', 'name', 'roll_no', 'face_encoding')
        students_list = []

        for student in students:
            students_list.append({
                'id': student['id'],
                'name': student['name'],
                'roll_no': student['roll_no'],
                'has_encoding': student['face_encoding'] is not None
            })

        return JsonResponse({
            'success': True,
            'students': students_list,
            'total': len(students_list)
        })

    except Exception as e:
        logger.error(f"Error getting students: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_http_methods(["POST"])
def load_encodings_view(request):
    """Load face encodings from management command"""
    try:
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({'success': False, 'message': 'Permission denied'})

        # Run load encodings command
        call_command('load_encodings', '--force')

        # Reload encodings in camera
        camera.load_face_encodings()

        return JsonResponse({
            'success': True,
            'message': 'Face encodings loaded successfully',
            'count': len(camera.known_face_encodings)
        })

    except Exception as e:
        logger.error(f"Error loading encodings: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_http_methods(["POST"])
def mark_attendance_api(request):
    """Manual attendance marking API"""
    try:
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({'success': False, 'message': 'Permission denied'})

        data = json.loads(request.body)
        student_id = data.get('student_id')
        status = data.get('status', 'present')
        notes = data.get('notes', 'Manual entry')

        if not student_id:
            return JsonResponse({'success': False, 'message': 'Student ID required'})

        student = Student.objects.get(id=student_id)
        attendance, created = Attendance.mark_attendance(
            student=student,
            status=status,
            notes=notes
        )

        action = 'created' if created else 'updated'
        return JsonResponse({
            'success': True,
            'message': f'Attendance {action} for {student.name}',
            'attendance_id': attendance.id
        })

    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student not found'})
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def manual_attendance(request):
    """Manual attendance entry page"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(
            request, 'You do not have permission to access this page.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status', 'present')
        notes = request.POST.get('notes', '')

        try:
            student = Student.objects.get(id=student_id)
            attendance, created = Attendance.mark_attendance(
                student=student,
                status=status,
                notes=f'Manual entry: {notes}' if notes else 'Manual entry'
            )

            action = 'marked' if created else 'updated'
            messages.success(
                request, f'Attendance {action} for {student.name}')

        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
        except Exception as e:
            messages.error(request, f'Error: {e}')

        return redirect('manual_attendance')

    # Get students and today's attendance
    students = Student.objects.all().order_by('roll_no')
    today_attendance = Attendance.objects.filter(
        date=date.today()).select_related('student')

    # Create attendance status dict
    attendance_status = {att.student.id: att for att in today_attendance}

    context = {
        'students': students,
        'attendance_status': attendance_status,
        'today_date': date.today(),
        'status_choices': Attendance.STATUS_CHOICES,
    }

    return render(request, 'attendance/manual_attendance.html', context)
