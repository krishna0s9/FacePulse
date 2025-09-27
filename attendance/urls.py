# attendance/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('take/', views.take_attendance, name='take_attendance'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('attendance_status/', views.attendance_status, name='attendance_status'),
    path('load-encodings/', views.load_encodings_view, name='load_encodings_view'),
    path('students/', views.students_api, name='students_api'),
]
