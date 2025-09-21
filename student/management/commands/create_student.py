from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import StudentProfile
from faculty.models import StudentClass


class Command(BaseCommand):
    help = 'Create a student user with profile'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str,
                            help='Username for the student')
        parser.add_argument('password', type=str,
                            help='Password for the student')
        parser.add_argument('--email', type=str,
                            help='Email for the student', default='')
        parser.add_argument('--first-name', type=str,
                            help='First name', default='')
        parser.add_argument('--last-name', type=str,
                            help='Last name', default='')
        parser.add_argument('--student-id', type=str,
                            help='Student ID', default='')
        parser.add_argument('--class-code', type=str,
                            help='Class code (e.g., CS101)', default='CS101')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        student_id = options['student_id'] or f"STU{User.objects.count() + 1:03d}"
        class_code = options['class_code']

        # Create or get the student class
        student_class, created = StudentClass.objects.get_or_create(
            code=class_code,
            defaults={
                'name': f'Class {class_code}',
                'description': f'Student class {class_code}'
            }
        )

        if created:
            self.stdout.write(f'Created new class: {student_class.name}')

        # Create the user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(f'Created user: {username}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {e}'))
            return

        # Create the student profile
        try:
            student_profile = StudentProfile.objects.create(
                user=user,
                student_id=student_id,
                student_class=student_class
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created student: {username} (ID: {student_id}) in class {student_class.name}'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error creating student profile: {e}'))
            # Clean up the user if profile creation failed
            user.delete()
