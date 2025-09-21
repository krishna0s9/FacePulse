from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from student.models import StudentProfile


@login_required
def role_based_redirect(request):
    """Redirect user to appropriate dashboard based on their role after login.

    - Admins (staff or superusers) → admin dashboard
    - Students (users with StudentProfile) → student dashboard
    - Others → fallback to neutral dashboard
    """
    user = request.user
    if not user or isinstance(user, AnonymousUser):
        return redirect('login')

    # Admin/staff has priority over any other role
    if user.is_superuser or user.is_staff:
        return redirect('admin_dashboard')

    # Student role is inferred by the presence of StudentProfile
    if StudentProfile.objects.filter(user=user).exists():
        return redirect('student_dashboard')

    # Unknown role – fallback to a neutral dashboard page
    return render(request, 'dashboard/index.html')


@login_required
def dashboard_view(request):
    """Redirect the logged-in user to the appropriate dashboard.

    - Admins (staff or superusers) go to the admin dashboard
    - Students (users with a StudentProfile) go to the student dashboard
    - Otherwise, show a neutral landing page
    """
    user = request.user
    if not user or isinstance(user, AnonymousUser):
        return redirect('login')

    # Admin/staff has priority over any other role
    if user.is_superuser or user.is_staff:
        return redirect('admin_dashboard')

    # Student role is inferred by the presence of StudentProfile
    if StudentProfile.objects.filter(user=user).exists():
        return redirect('student_dashboard')

    # Unknown role – fallback to a neutral dashboard page if desired
    return render(request, 'dashboard/index.html')
