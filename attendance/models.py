# attendance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import json


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    face_encoding = ArrayField(
        models.FloatField(),
        size=128,
        null=True,
        blank=True,
        help_text="128-dimensional face encoding"
    )
    image = models.ImageField(upload_to='students/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_no']
        indexes = [
            models.Index(fields=['roll_no']),
        ]

    def __str__(self):
        return f"{self.roll_no} - {self.name}"

    def has_face_encoding(self):
        """Check if student has face encoding"""
        return self.face_encoding is not None and len(self.face_encoding) == 128

    def get_attendance_percentage(self, days=30):
        """Calculate attendance percentage for given days"""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        total_records = self.attendance_set.filter(
            date__gte=start_date,
            date__lte=end_date
        ).count()

        if total_records == 0:
            return 0

        present_records = self.attendance_set.filter(
            date__gte=start_date,
            date__lte=end_date,
            status='present'
        ).count()

        return round((present_records / total_records) * 100, 2)


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='present')
    marked_at = models.DateTimeField(default=timezone.now, blank=True)
    confidence = models.FloatField(
        null=True, blank=True, help_text="Face recognition confidence")
    notes = models.TextField(blank=True, help_text="Additional notes")

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', '-marked_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

    @classmethod
    def mark_attendance(cls, student, status='present', confidence=None, notes=''):
        """Mark attendance for a student"""
        attendance, created = cls.objects.update_or_create(
            student=student,
            date=timezone.now().date(),
            defaults={
                'status': status,
                'marked_at': timezone.now(),
                'confidence': confidence,
                'notes': notes,
            }
        )
        return attendance, created


class AttendanceSession(models.Model):
    """Track attendance sessions"""
    name = models.CharField(
        max_length=100, help_text="Session name (e.g., Morning Class)")
    date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_recognized = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.name} - {self.date}"

    def end_session(self):
        """End the attendance session"""
        self.end_time = timezone.now()
        self.is_active = False
        self.save()
