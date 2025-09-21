# from django.db import models
# from django.contrib.auth.models import User

#class Student(models.Model):
 #   user = models.OneToOneField(User, on_delete=models.CASCADE)
    # You can add more fields if needed:
    # roll_number = models.CharField(max_length=20, unique=True)
    # branch = models.CharField(max_length=50)

  #  def __str__(self):
   #     return self.user.username


#class Attendance(models.Model):
 #   student = models.ForeignKey(Student, on_delete=models.CASCADE)
  #  date = models.DateField(auto_now_add=True)
   # status = models.CharField(max_length=10)

    #def __str__(self):
     #   return f"{self.student.user.username} - {self.date} - {self.status}"
