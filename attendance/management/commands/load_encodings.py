# attendance/management/commands/load_encodings.py
import os
import face_recognition
import numpy as np
from PIL import Image
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from attendance.models import Student
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Load face encodings from student images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload encodings even if they already exist',
        )
        parser.add_argument(
            '--directory',
            type=str,
            default='media/students/',
            help='Directory containing student images (default: media/students/)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting face encoding extraction...')
        )

        force = options['force']
        image_directory = options['directory']

        if not os.path.exists(image_directory):
            raise CommandError(
                f'Directory "{image_directory}" does not exist.')

        # Get all image files
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        image_files = []

        for filename in os.listdir(image_directory):
            if filename.lower().endswith(supported_formats):
                image_files.append(filename)

        if not image_files:
            self.stdout.write(
                self.style.WARNING(
                    f'No image files found in {image_directory}')
            )
            return

        self.stdout.write(f'Found {len(image_files)} image files')

        successful_encodings = 0
        failed_encodings = 0
        skipped_encodings = 0

        for filename in image_files:
            try:
                # Parse filename for student information
                # Expected format: STU001_John_Doe.jpg or 001_John_Doe.jpg
                name_part = os.path.splitext(filename)[0]

                if name_part.startswith('STU'):
                    # Extract roll number and name from STU001_John_Doe format
                    parts = name_part.split('_', 1)
                    if len(parts) >= 2:
                        roll_no = parts[0].replace('STU', '').zfill(3)
                        student_name = parts[1].replace('_', ' ')
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping {filename}: Invalid filename format')
                        )
                        continue
                else:
                    # Try format: 001_John_Doe.jpg
                    parts = name_part.split('_', 1)
                    if len(parts) >= 2 and parts[0].isdigit():
                        roll_no = parts[0].zfill(3)
                        student_name = parts[1].replace('_', ' ')
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Skipping {filename}: Invalid filename format')
                        )
                        continue

                # Check if student exists or create
                student = self.get_or_create_student(roll_no, student_name)

                # Skip if encoding exists and not forcing
                if student.face_encoding and not force:
                    self.stdout.write(
                        f'Skipping {student.name}: Encoding already exists')
                    skipped_encodings += 1
                    continue

                # Load and process image
                image_path = os.path.join(image_directory, filename)
                encoding = self.extract_face_encoding(image_path)

                if encoding is not None:
                    # Save encoding to database
                    student.face_encoding = encoding.tolist()
                    # Store relative path
                    student.image = f'students/{filename}'
                    student.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Processed {student.name} ({roll_no})')
                    )
                    successful_encodings += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to extract face from {filename}')
                    )
                    failed_encodings += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {filename}: {e}')
                )
                failed_encodings += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(
            f'Face encoding extraction complete!'))
        self.stdout.write(f'Successful: {successful_encodings}')
        self.stdout.write(f'Failed: {failed_encodings}')
        self.stdout.write(f'Skipped: {skipped_encodings}')
        self.stdout.write(f'Total processed: {len(image_files)}')

        if successful_encodings > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nFace encodings have been loaded successfully!'
                    '\nYou can now start the attendance system.'
                )
            )

    def get_or_create_student(self, roll_no, student_name):
        """Get existing student or create new one"""
        try:
            # Try to find student by roll number
            student = Student.objects.get(roll_no=roll_no)

            # Update name if different
            if student.name != student_name:
                self.stdout.write(
                    self.style.WARNING(
                        f'Updating name for {roll_no}: {student.name} -> {student_name}'
                    )
                )
                student.name = student_name
                student.save()

            return student

        except Student.DoesNotExist:
            # Create new user and student
            username = f"student_{roll_no}"

            # Check if user exists
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': student_name.split()[0] if student_name.split() else student_name,
                    'last_name': ' '.join(student_name.split()[1:]) if len(student_name.split()) > 1 else '',
                    'email': f'{username}@student.edu',
                }
            )

            # Create student profile
            student = Student.objects.create(
                user=user,
                name=student_name,
                roll_no=roll_no
            )

            if user_created:
                self.stdout.write(
                    f'Created new user and student: {student_name} ({roll_no})')
            else:
                self.stdout.write(
                    f'Created student profile for existing user: {student_name} ({roll_no})')

            return student

    def extract_face_encoding(self, image_path):
        """Extract face encoding from image"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)

            # Find face locations
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'No face found in {os.path.basename(image_path)}')
                )
                return None

            if len(face_locations) > 1:
                self.stdout.write(
                    self.style.WARNING(
                        f'Multiple faces found in {os.path.basename(image_path)}, using first one'
                    )
                )

            # Extract face encodings
            face_encodings = face_recognition.face_encodings(
                image, face_locations)

            if len(face_encodings) > 0:
                return face_encodings[0]  # Return first encoding
            else:
                return None

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error processing {os.path.basename(image_path)}: {e}')
            )
            return None

    def validate_encoding(self, encoding):
        """Validate face encoding"""
        if encoding is None:
            return False

        if not isinstance(encoding, np.ndarray):
            return False

        if encoding.shape != (128,):
            return False

        # Check if encoding contains valid values
        if np.isnan(encoding).any() or np.isinf(encoding).any():
            return False

        return True
