from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import StudentProfile


class Command(BaseCommand):
    help = 'List all users and their roles'

    def handle(self, *args, **options):
        self.stdout.write("Users and their roles:")
        self.stdout.write("-" * 50)

        for user in User.objects.all():
            role = "Unknown"
            if user.is_superuser:
                role = "Superuser"
            elif user.is_staff:
                role = "Staff/Admin"
            elif StudentProfile.objects.filter(user=user).exists():
                role = "Student"
                try:
                    profile = StudentProfile.objects.get(user=user)
                    role += f" (ID: {profile.student_id})"
                except:
                    pass

            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Name: {user.get_full_name() or 'N/A'}")
            self.stdout.write(f"Role: {role}")
            self.stdout.write(f"Active: {user.is_active}")
            self.stdout.write("-" * 30)
