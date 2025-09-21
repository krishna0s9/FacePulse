import cv2
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Student, Attendance
import threading
import time
import json
import os
from PIL import Image
import face_recognition


class FaceRecognitionCamera:
    def __init__(self):
        self.camera = None
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roll_nos = []
        self.attendance_marked = set()
        self.tolerance = 0.5  # Face recognition tolerance
        self.load_known_faces()

    def load_known_faces(self):
        """Load face encodings from database"""
        students = Student.objects.filter(face_encoding__isnull=False)
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roll_nos = []

        for student in students:
            if student.face_encoding:
                # Convert list to numpy array
                face_encoding = np.array(student.face_encoding)
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(student.name)
                self.known_face_roll_nos.append(student.roll_no)

    def mark_attendance(self, roll_no, name):
        """Mark attendance for a student"""
        if roll_no in self.attendance_marked:
            return False

        try:
            student = Student.objects.get(roll_no=roll_no)
            today = timezone.now().date()

            # Check if attendance already marked today
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=today,
                defaults={'status': 'present'}
            )

            if created:
                self.attendance_marked.add(roll_no)
                return True
            else:
                return False
        except Student.DoesNotExist:
            return False

    def get_frame(self):
        """Get frame from camera with face recognition"""
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        ret, frame = self.camera.read()
        if not ret:
            return None

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, tolerance=self.tolerance)
            name = "Unknown"
            roll_no = "Unknown"

            # Find the best match
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    roll_no = self.known_face_roll_nos[best_match_index]

                    # Mark attendance if not already marked
                    if roll_no not in self.attendance_marked:
                        if self.mark_attendance(roll_no, name):
                            print(f"Attendance marked for {name} ({roll_no})")

            face_names.append(name)

        # Draw rectangles and labels
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw rectangle around face
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw label
            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        font, 0.6, (255, 255, 255), 1)

        # Add instruction text
        cv2.putText(frame, 'Press Q to quit', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f'Marked: {len(self.attendance_marked)}', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f'Known Faces: {len(self.known_face_encodings)}', (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame

    def release(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            self.camera = None


# Global camera instance
camera_instance = None


def take_attendance(request):
    """Main view for taking attendance"""
    if request.method == 'GET':
        return render(request, 'attendance/take_attendance.html')

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def video_feed(request):
    """Video feed for webcam"""
    global camera_instance

    if camera_instance is None:
        camera_instance = FaceRecognitionCamera()

    def generate_frames():
        while True:
            frame = camera_instance.get_frame()
            if frame is None:
                break

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                break

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


def stop_camera(request):
    """Stop camera and release resources"""
    global camera_instance

    if camera_instance:
        camera_instance.release()
        camera_instance = None

    return JsonResponse({'status': 'success', 'message': 'Camera stopped'})


def attendance_status(request):
    """Get current attendance status"""
    global camera_instance

    if camera_instance:
        marked_count = len(camera_instance.attendance_marked)
        total_students = len(camera_instance.known_face_encodings)

        return JsonResponse({
            'status': 'success',
            'marked_count': marked_count,
            'total_students': total_students,
            'marked_students': list(camera_instance.attendance_marked)
        })

    return JsonResponse({'status': 'error', 'message': 'Camera not initialized'})


def manual_attendance(request):
    """Manual attendance marking for testing"""
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')
        if roll_no:
            try:
                student = Student.objects.get(roll_no=roll_no)
                today = timezone.now().date()

                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=today,
                    defaults={'status': 'present'}
                )

                if created:
                    messages.success(
                        request, f'Attendance marked for {student.name}')
                else:
                    messages.info(
                        request, f'Attendance already marked for {student.name}')

            except Student.DoesNotExist:
                messages.error(
                    request, f'Student with roll number {roll_no} not found')

        return redirect('take_attendance')

    return render(request, 'attendance/manual_attendance.html')
