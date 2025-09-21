import os
from django.core.management.base import BaseCommand
from django.conf import settings
from attendance.models import Student
from PIL import Image
import numpy as np
import face_recognition


class Command(BaseCommand):
    help = 'Load face encodings from images in media/students/ directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload encodings even if they already exist',
        )

    def handle(self, *args, **options):
        media_dir = os.path.join(settings.MEDIA_ROOT, 'students')

        if not os.path.exists(media_dir):
            self.stdout.write(
                self.style.WARNING(
                    f'Directory {media_dir} does not exist. Creating it...')
            )
            os.makedirs(media_dir, exist_ok=True)
            return

        # Get all image files from the directory
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        image_files = []

        for filename in os.listdir(media_dir):
            if filename.lower().endswith(image_extensions):
                image_files.append(filename)

        if not image_files:
            self.stdout.write(
                self.style.WARNING(f'No image files found in {media_dir}')
            )
            return

        self.stdout.write(f'Found {len(image_files)} image files')

        processed_count = 0
        error_count = 0

        for filename in image_files:
            try:
                # Extract student info from filename (assuming format: roll_no_name.jpg)
                name_without_ext = os.path.splitext(filename)[0]

                # Try to parse roll_no and name from filename
                parts = name_without_ext.split('_', 1)
                if len(parts) >= 2:
                    roll_no = parts[0]
                    name = parts[1].replace('_', ' ')
                else:
                    # If no underscore, use filename as name and generate roll_no
                    name = name_without_ext.replace('_', ' ')
                    roll_no = f"STU{processed_count + 1:03d}"

                # Check if student already exists
                try:
                    student = Student.objects.get(roll_no=roll_no)
                except Student.DoesNotExist:
                    # Create a User first
                    from django.contrib.auth.models import User
                    username = f"student_{roll_no.lower()}"
                    user, user_created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': name.split()[0] if name.split() else name,
                            'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                            'email': f"{username}@example.com"
                        }
                    )

                    # Create Student
                    student = Student.objects.create(
                        user=user,
                        name=name,
                        roll_no=roll_no,
                        image=f'students/{filename}'
                    )

                # Skip if encoding already exists and not forcing
                if student.face_encoding and not options['force']:
                    self.stdout.write(
                        f'Skipping {filename} - encoding already exists')
                    continue

                # Load and process the image
                image_path = os.path.join(media_dir, filename)

                # Validate image file
                try:
                    with Image.open(image_path) as img:
                        img.verify()
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Invalid image file {filename}: {e}')
                    )
                    error_count += 1
                    continue

                # Extract face encoding using face_recognition library
                try:
                    # Load the image using face_recognition
                    face_image = face_recognition.load_image_file(image_path)

                    # Find face locations in the image
                    face_locations = face_recognition.face_locations(
                        face_image)

                    if len(face_locations) == 0:
                        self.stdout.write(
                            self.style.WARNING(f'No face found in {filename}')
                        )
                        error_count += 1
                        continue
                    elif len(face_locations) > 1:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Multiple faces found in {filename}, using the first one')
                        )

                    # Get face encodings
                    face_encodings = face_recognition.face_encodings(
                        face_image, face_locations)

                    if len(face_encodings) == 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Could not encode face in {filename}')
                        )
                        error_count += 1
                        continue

                    # Use the first face encoding
                    face_encoding = face_encodings[0].tolist()

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error processing face in {filename}: {str(e)}')
                    )
                    error_count += 1
                    continue

                # Update student with image and face encoding
                student.image = f'students/{filename}'
                student.face_encoding = face_encoding
                student.save()

                processed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed {filename} -> {student.name} ({student.roll_no})')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {filename}: {str(e)}')
                )
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Completed! Processed: {processed_count}, Errors: {error_count}'
            )
        )
