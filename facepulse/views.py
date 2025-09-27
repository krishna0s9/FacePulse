# facepulse/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import connection
from attendance.models import Student, Attendance
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'registration/login.html')


@login_required
def dashboard_redirect(request):
    """Redirect users to appropriate dashboard based on their role"""
    try:
        # Check if user is admin/staff
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')

        # Check if user has a student profile
        try:
            student = Student.objects.get(user=request.user)
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            # If user exists but no student profile, create one
            student = Student.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                roll_no=f"STU{request.user.id:03d}"
            )
            messages.info(request, 'Student profile created successfully!')
            return redirect('student_dashboard')

    except Exception as e:
        logger.error(f"Dashboard redirect error: {e}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('home')


@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    try:
        # Verify user has admin permissions
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(
                request, 'You do not have permission to access the admin dashboard.')
            return redirect('student_dashboard')

        # Get dashboard statistics with error handling
        context = get_admin_dashboard_context()
        return render(request, 'dashboard/admin_dashboard.html', context)

    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        messages.error(request, 'Error loading admin dashboard.')
        return render(request, 'dashboard/admin_dashboard.html', {'error': True})


@login_required
def student_dashboard(request):
    """Student dashboard view"""
    try:
        # Get or create student profile
        student, created = Student.objects.get_or_create(
            user=request.user,
            defaults={
                'name': request.user.get_full_name() or request.user.username,
                'roll_no': f"STU{request.user.id:03d}"
            }
        )

        if created:
            messages.info(
                request, 'Welcome! Your student profile has been created.')

        # Get student's attendance data with error handling
        context = get_student_dashboard_context(student)
        return render(request, 'dashboard/student_dashboard.html', context)

    except Exception as e:
        logger.error(f"Student dashboard error: {e}")
        messages.error(request, 'Error loading student dashboard.')
        return render(request, 'dashboard/student_dashboard.html', {'error': True})


def get_admin_dashboard_context():
    """Get context data for admin dashboard with error handling"""
    try:
        total_students = Student.objects.count()
        today = date.today()

        # Today's attendance with safe handling
        today_attendance = Attendance.objects.filter(date=today)
        present_today = today_attendance.filter(status='present').count()
        absent_today = max(0, total_students - present_today)

        # This week's attendance (last 7 days)
        week_start = today - timedelta(days=7)
        week_attendance = Attendance.objects.filter(
            date__gte=week_start,
            date__lte=today,
            status='present'
        ).values('date').distinct().count()

        # Recent attendance records with safe handling
        recent_attendance = Attendance.objects.select_related(
            'student').order_by('-marked_at')[:10]

        # Calculate percentage safely
        if total_students > 0:
            attendance_percentage = round(
                (present_today / total_students * 100), 2)
        else:
            attendance_percentage = 0

        context = {
            'total_students': total_students,
            'present_today': present_today,
            'absent_today': absent_today,
            'attendance_percentage': attendance_percentage,
            'week_attendance_days': week_attendance,
            'recent_attendance': recent_attendance,
            'today_date': today,
        }

        return context

    except Exception as e:
        logger.error(f"Admin dashboard context error: {e}")
        return {
            'total_students': 0,
            'present_today': 0,
            'absent_today': 0,
            'attendance_percentage': 0,
            'error': True,
            'today_date': date.today(),
        }


def get_student_dashboard_context(student):
    """Get context data for student dashboard with error handling"""
    try:
        # Get student's attendance records safely
        attendance_records = Attendance.objects.filter(
            student=student).order_by('-date')[:30]

        # Calculate attendance statistics safely
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()

        if total_days > 0:
            attendance_percentage = round((present_days / total_days * 100), 2)
        else:
            attendance_percentage = 0

        # This month's attendance
        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_attendance = Attendance.objects.filter(
            student=student,
            date__gte=month_start,
            date__lte=today
        )
        month_present = month_attendance.filter(status='present').count()
        month_total = month_attendance.count()

        if month_total > 0:
            month_percentage = round((month_present / month_total * 100), 2)
        else:
            month_percentage = 0

        context = {
            'student': student,
            'attendance_records': attendance_records,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': total_days - present_days,
            'attendance_percentage': attendance_percentage,
            'month_present': month_present,
            'month_total': month_total,
            'month_percentage': month_percentage,
        }

        return context

    except Exception as e:
        logger.error(f"Student dashboard context error: {e}")
        return {
            'student': student,
            'error': True,
            'attendance_records': [],
            'total_days': 0,
            'present_days': 0,
            'attendance_percentage': 0,
        }
