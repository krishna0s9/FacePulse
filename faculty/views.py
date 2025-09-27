from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


# ---------------- Custom Login View ---------------- #

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        """Redirect user based on role after login."""
        from student.models import StudentProfile   # ✅ import inside function
        user = self.request.user
        if user.is_staff or user.is_superuser:   # Admin/staff
            return reverse_lazy('admin_dashboard')
        elif StudentProfile.objects.filter(user=user).exists():  # Student
            return reverse_lazy('student_dashboard')
        else:   # ✅ Fallback → login page
            return reverse_lazy('login')


# ---------------- Helper Functions ---------------- #

def _is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _is_student(user):
    from student.models import StudentProfile   # ✅ import inside function
    return user.is_authenticated and StudentProfile.objects.filter(user=user).exists()


# ---------------- Admin Dashboard ---------------- #

@login_required
@user_passes_test(_is_admin)
def admin_dashboard(request):
    from attendance.models import Attendance   # ✅ import from attendance app
    attendance_records = Attendance.objects.select_related(
        'student', 'student__user'
    )[:10]
    return render(request, 'dashboard/admin_dashboard.html', {
        'attendance_records': attendance_records
    })


# ---------------- Student Dashboard ---------------- #

@login_required
@user_passes_test(_is_student)
def student_dashboard(request):
    from student.models import Attendance, StudentProfile   # ✅ import inside function
    student_profile = StudentProfile.objects.select_related(
        'user', 'student_class'
    ).get(user=request.user)
    my_attendance = Attendance.objects.filter(
        student=student_profile
    ).select_related('student_class').order_by('-date')

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


# ---------------- Attendance Taking ---------------- #

@require_POST
@login_required
@user_passes_test(_is_admin)
def take_attendance(request):
    # Import only if needed
    from student.models import Attendance
    image = request.FILES.get('image')

    if not image:
        return redirect('admin_dashboard')

    # TODO: Face recognition and attendance logic
    return redirect('admin_dashboard')
