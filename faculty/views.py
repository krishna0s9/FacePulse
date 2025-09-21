from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from student.models import Attendance, StudentProfile

# ---------------- Existing Views ---------------- #


def _is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(_is_admin)
def admin_dashboard(request):
    """Admin dashboard with recent attendance overview.

    Only accessible by staff/superusers.
    """
    attendance_records = Attendance.objects.select_related(
        'student', 'student__user', 'student_class')[:10]
    return render(request, 'dashboard/admin_dashboard.html', {
        'attendance_records': attendance_records
    })


def _is_student(user):
    return user.is_authenticated and StudentProfile.objects.filter(user=user).exists()


@login_required
@user_passes_test(_is_student)
def student_dashboard(request):
    """Student dashboard showing personal attendance and summary.

    Only accessible by users who have a StudentProfile.
    """
    student_profile = StudentProfile.objects.select_related(
        'user', 'student_class').get(user=request.user)
    my_attendance = Attendance.objects.filter(
        student=student_profile).select_related('student_class').order_by('-date')

    total_days = my_attendance.count()
    present_count = my_attendance.filter(status='present').count()
    absent_count = my_attendance.filter(status='absent').count()
    percentage = round((present_count / total_days) *
                       100, 2) if total_days else 0.0

    return render(request, 'dashboard/student_dashboard.html', {
        'student': student_profile,
        'my_attendance': my_attendance,
        'total_days': total_days,
        'present_count': present_count,
        'absent_count': absent_count,
        'percentage': percentage,
    })


@require_POST
@login_required
@user_passes_test(_is_admin)
def take_attendance(request):
    image = request.FILES.get('image')

    if not image:
        return redirect('admin_dashboard')

    # TODO: Face recognition and attendance logic
    return redirect('admin_dashboard')
