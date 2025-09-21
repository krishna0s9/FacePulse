from django.contrib import admin

# Register your models here.
# faculty/admin.py - UPDATE THIS EXISTING FILE
from django.contrib import admin
from .models import StudentClass, AttendanceReport

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'start_date', 'end_date', 'generated_by']
    list_filter = ['report_type', 'generated_at']
    date_hierarchy = 'generated_at'