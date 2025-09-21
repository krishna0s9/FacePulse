from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    face_encoding = ArrayField(
        models.FloatField(), size=128, null=True, blank=True)
    image = models.ImageField(upload_to='students/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='present')
    marked_at = models.DateTimeField(default=timezone.now, blank=True)
    confidence = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', '-marked_at']

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
