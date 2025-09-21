from django.contrib import admin
from django.urls import path
from faculty import views as faculty_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Admin Dashboard
    path('dashboard/', faculty_views.admin_dashboard, name='admin_dashboard'),

    # Student Dashboard
    path('dashboard/student/', faculty_views.student_dashboard, name='student_dashboard'),

    # ✅ Add this for take_attendance form to work
    path('dashboard/take-attendance/', faculty_views.take_attendance, name='take_attendance'),
]
