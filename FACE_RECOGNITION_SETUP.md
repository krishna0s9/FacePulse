# FacePulse - Face Recognition Attendance System

## Module 4: Face Recognition with OpenCV + face_recognition

This module implements a complete face recognition attendance system using OpenCV and the face_recognition library.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirement.txt
```

### 2. Database Migration

```bash
python manage.py makemigrations attendance
python manage.py migrate
```

### 3. Load Student Face Encodings

1. Place student images in the `media/students/` directory
2. Name the images using the format: `roll_no_name.jpg` (e.g., `001_John_Doe.jpg`)
3. Run the management command to load face encodings:

```bash
python manage.py load_encodings
```

### 4. Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 5. Run the Server

```bash
python manage.py runserver
```

## Usage

1. **Admin Dashboard**: Navigate to `/dashboard/admin/` and click "Take Attendance with Camera"
2. **Face Recognition**: The system will:
   - Open your webcam
   - Detect faces in real-time
   - Compare faces with stored encodings
   - Automatically mark attendance for recognized students
   - Show names with checkmarks for marked students

## Features

- **Real-time Face Recognition**: Uses OpenCV for webcam access and face_recognition for face matching
- **Automatic Attendance Marking**: Recognized students are automatically marked as "Present"
- **Tolerance Control**: Face matching uses a tolerance of 0.5 for accuracy
- **Real-time Status**: Shows count of marked students and total students
- **Database Integration**: All attendance records are saved to the database
- **Admin Interface**: Full Django admin interface for managing students and attendance

## File Structure

```
attendance/
├── models.py              # Student and Attendance models
├── views.py               # Face recognition views and camera handling
├── urls.py                # URL patterns
├── admin.py               # Django admin configuration
└── management/
    └── commands/
        └── load_encodings.py  # Command to load face encodings

templates/
└── attendance/
    └── take_attendance.html   # Main attendance interface

media/
└── students/              # Directory for student images
```

## API Endpoints

- `GET /attendance/take/` - Main attendance page
- `GET /attendance/video_feed/` - Live video stream with face recognition
- `POST /attendance/stop_camera/` - Stop camera and release resources
- `GET /attendance/attendance_status/` - Get current attendance status

## Models

### Student Model
- `name`: Student's full name
- `roll_no`: Unique roll number
- `face_encoding`: 128-dimensional face encoding array
- `image`: Student's photo
- `user`: Associated Django user

### Attendance Model
- `student`: Foreign key to Student
- `date`: Date of attendance
- `status`: Present/Absent/Late
- `marked_at`: Timestamp when marked
- `confidence`: Recognition confidence score

## Management Commands

### load_encodings
Loads face encodings from images in `media/students/` directory.

```bash
python manage.py load_encodings [--force]
```

Options:
- `--force`: Force reload encodings even if they already exist

## Troubleshooting

1. **Camera not working**: Ensure your webcam is connected and not being used by other applications
2. **Face not detected**: Make sure the image has a clear, front-facing photo of the person
3. **Low recognition accuracy**: Try using higher quality images or adjusting the tolerance in the code
4. **Database errors**: Ensure PostgreSQL is running and the database is properly configured

## Security Notes

- This system is designed for development/testing purposes
- In production, implement proper authentication and authorization
- Consider adding rate limiting and security headers
- Store face encodings securely and consider encryption
