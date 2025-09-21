from django.contrib import admin
from .models import Student, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_no', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'roll_no', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_at')
    list_filter = ('date', 'status', 'marked_at')
    search_fields = ('student__name', 'student__roll_no')
    readonly_fields = ('marked_at',)
    date_hierarchy = 'date'
