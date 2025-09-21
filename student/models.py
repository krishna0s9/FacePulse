from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from faculty.models import StudentClass  # Import from faculty app

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    image = models.ImageField(upload_to='student_images/', null=True, blank=True)
    encoding = models.BinaryField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    image = models.ImageField(upload_to='attendance_images/', null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

class RecognitionLog(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('multiple', 'Multiple Faces'),
        ('none', 'No Face Detected'),
    )
    
    image = models.ImageField(upload_to='recognition_logs/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.status} - {self.created_at}"