from django.contrib import admin

# Register your models here.
# student/admin.py - UPDATE THIS EXISTING FILE
from django.contrib import admin
from .models import StudentProfile, Attendance, RecognitionLog

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'student_class', 'is_active']
    list_filter = ['student_class', 'is_active']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'confidence']
    list_filter = ['status', 'date', 'student_class']
    date_hierarchy = 'date'

@admin.register(RecognitionLog)
class RecognitionLogAdmin(admin.ModelAdmin):
    list_display = ['status', 'student', 'confidence', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']