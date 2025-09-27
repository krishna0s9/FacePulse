# FacePulse - Face Recognition Attendance System

## Technical Documentation

### Project Overview

FacePulse is a comprehensive Django-based face recognition attendance system that leverages OpenCV and the face_recognition library to automatically mark student attendance through real-time facial recognition. The system provides role-based access control, web-based interfaces, and seamless integration with PostgreSQL database.

### Architecture

#### Technology Stack
- **Backend Framework**: Django 5.2.6
- **Database**: PostgreSQL
- **Face Recognition**: face_recognition library (1.3.0)
- **Computer Vision**: OpenCV (4.8.1)
- **Image Processing**: Pillow (10.4.0)
- **Frontend**: HTML5, CSS3, JavaScript
- **Template Engine**: Django Templates
- **Web Server**: Django Development Server (Development)

#### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │────│   Django App    │────│   PostgreSQL    │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              │
                       ┌─────────────────┐
                       │  Face Recognition│
                       │  (OpenCV +      │
                       │   face_recognition)│
                       └─────────────────┘
```

### Project Structure

```
FacePulse/
├── facepulse/                 # Main Django project
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── views.py             # Main project views
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── attendance/               # Attendance management app
│   ├── models.py            # Student & Attendance models
│   ├── views.py             # Face recognition views
│   ├── urls.py              # Attendance URLs
│   ├── admin.py             # Admin interface
│   └── management/
│       └── commands/
│           └── load_encodings.py  # Face encoding extraction
├── student/                  # Student management app
│   ├── models.py            # StudentProfile model
│   ├── views.py             # Student views
│   └── management/
│       └── commands/        # Custom management commands
├── faculty/                  # Faculty management app
│   ├── models.py            # Faculty models
│   ├── views.py             # Faculty views
│   └── urls.py              # Faculty URLs
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── registration/        # Authentication templates
│   ├── dashboard/           # Dashboard templates
│   └── attendance/          # Attendance templates
├── media/                    # Media files
│   └── students/            # Student images for training
├── staticfiles/             # Collected static files
├── venv/                    # Virtual environment
├── manage.py                # Django management script
└── requirements.txt         # Python dependencies
```

### Core Components

#### 1. Face Recognition Engine

**Location**: `attendance/views.py`

The face recognition system is implemented in the `FaceRecognitionCamera` class:

```python
class FaceRecognitionCamera:
    def __init__(self):
        self.camera = None
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roll_nos = []
        self.attendance_marked = set()
        self.tolerance = 0.5  # Face recognition tolerance
```

**Key Features**:
- Real-time face detection using OpenCV
- Face encoding extraction using face_recognition library
- Face matching with configurable tolerance (0.5)
- Automatic attendance marking for recognized faces
- Visual feedback with colored bounding boxes

#### 2. Database Models

**Student Model** (`attendance/models.py`):
```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    face_encoding = ArrayField(models.FloatField(), size=128, null=True, blank=True)
    image = models.ImageField(upload_to='students/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Attendance Model** (`attendance/models.py`):
```python
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_at = models.DateTimeField(default=timezone.now, blank=True)
    confidence = models.FloatField(null=True, blank=True)
```

#### 3. Face Encoding Management

**Management Command**: `python manage.py load_encodings`

The system includes a custom Django management command that:
- Scans the `media/students/` directory for student images
- Extracts face encodings using the face_recognition library
- Stores 128-dimensional face encodings in the database
- Handles multiple faces in images (uses first detected face)
- Supports various image formats (JPG, PNG, BMP, TIFF)

#### 4. Web Interface

**Main Attendance Page**: `/attendance/take/`
- Real-time webcam feed
- Face detection visualization
- Attendance status display
- Start/Stop camera controls
- Keyboard shortcuts (Q to quit, S/Space to capture)

**Dashboard System**:
- Role-based access control
- Admin dashboard for faculty
- Student dashboard for students
- Automatic role detection based on user permissions

### API Endpoints

#### Authentication
- `GET /accounts/login/` - Login page
- `POST /accounts/login/` - Login processing
- `GET /accounts/logout/` - Logout

#### Attendance System
- `GET /attendance/take/` - Main attendance interface
- `GET /attendance/video_feed/` - Live camera stream
- `POST /attendance/stop_camera/` - Stop camera
- `GET /attendance/attendance_status/` - Get attendance status

#### Dashboards
- `GET /dashboard/` - Role-based dashboard redirect
- `GET /dashboard/admin/` - Admin dashboard
- `GET /dashboard/student/` - Student dashboard

### Configuration

#### Django Settings (`facepulse/settings.py`)

**Database Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'facepulse',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}
```

**Static Files Configuration**:
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**Media Files Configuration**:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### Security Settings
- `DEBUG = True` (Development only)
- `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']`
- CSRF protection enabled
- Session-based authentication

### Installation & Setup

#### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- CMake
- Visual Studio C++ Build Tools (for dlib compilation)

#### Installation Steps

1. **Clone and Setup Environment**:
```bash
cd FacePulse
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # Linux/Mac
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Database Setup**:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. **Collect Static Files**:
```bash
python manage.py collectstatic --noinput
```

5. **Start Development Server**:
```bash
python manage.py runserver
```

### Usage Workflow

#### 1. Training Phase
1. Place student images in `media/students/` with naming convention: `STU001_John_Doe.jpg`
2. Run face encoding extraction: `python manage.py load_encodings`
3. Verify encodings are stored in database

#### 2. Attendance Taking
1. Navigate to `/attendance/take/`
2. Click "Start Camera" to begin face recognition
3. Students look at camera for automatic recognition
4. System marks attendance for recognized faces
5. Click "Stop Camera" or press 'Q' to finish

#### 3. Monitoring
1. Access admin dashboard at `/admin/`
2. View attendance records in database
3. Monitor system performance and accuracy

### Performance Considerations

#### Face Recognition Optimization
- **Frame Resizing**: Images are resized to 25% for faster processing
- **Tolerance Setting**: Configurable face matching tolerance (default: 0.5)
- **Batch Processing**: Face encodings are loaded once per session
- **Memory Management**: Proper camera resource cleanup

#### Database Optimization
- **Indexed Fields**: `roll_no` and `date` fields are indexed
- **Unique Constraints**: Prevents duplicate attendance records
- **ArrayField**: Efficient storage of 128-dimensional face encodings

### Security Features

#### Authentication & Authorization
- Django's built-in authentication system
- Role-based access control (Admin/Student)
- Session-based security
- CSRF protection on all forms

#### Data Protection
- Secure file upload handling
- Input validation and sanitization
- SQL injection prevention through Django ORM
- XSS protection through template escaping

### Error Handling

#### Face Recognition Errors
- No face detected: Graceful handling with user feedback
- Multiple faces: Uses first detected face with warning
- Camera access issues: Clear error messages
- Database connection errors: Fallback mechanisms

#### Web Interface Errors
- 404 errors: Custom error pages
- 500 errors: Debug information in development
- Static file serving: Fallback to development server

### Testing

#### Test Script
The project includes `test_face_recognition.py` for comprehensive testing:
- Package import verification
- Camera access testing
- Face recognition functionality testing
- Database connectivity testing

#### Manual Testing
- Face recognition accuracy testing
- Web interface functionality testing
- Cross-browser compatibility testing
- Performance testing under load

### Deployment Considerations

#### Production Requirements
- WSGI/ASGI server (Gunicorn/Uvicorn)
- Reverse proxy (Nginx)
- Static file serving
- Database connection pooling
- SSL/TLS encryption
- Environment variable configuration

#### Scalability
- Horizontal scaling with load balancers
- Database replication for high availability
- CDN for static file delivery
- Caching strategies for face encodings

### Troubleshooting

#### Common Issues

1. **Camera Not Working**:
   - Check camera permissions
   - Verify camera is not used by other applications
   - Test with `test_face_recognition.py`

2. **Face Recognition Not Working**:
   - Ensure face encodings are loaded: `python manage.py load_encodings`
   - Check image quality and lighting
   - Verify face_recognition library installation

3. **Admin Blank Page**:
   - Check static files: `python manage.py collectstatic`
   - Verify LOGIN_REDIRECT_URL setting
   - Check browser console for JavaScript errors

4. **Database Connection Issues**:
   - Verify PostgreSQL is running
   - Check database credentials in settings.py
   - Run migrations: `python manage.py migrate`

### Future Enhancements

#### Planned Features
- Real-time notifications
- Attendance reports and analytics
- Mobile app integration
- Multi-classroom support
- Advanced face recognition models
- Cloud deployment support

#### Technical Improvements
- API rate limiting
- Caching layer implementation
- Background task processing
- Microservices architecture
- Container deployment (Docker)

### Support & Maintenance

#### Logging
- Django logging configuration
- Face recognition accuracy metrics
- Performance monitoring
- Error tracking and reporting

#### Backup Strategy
- Database backup procedures
- Media file backup
- Configuration backup
- Disaster recovery planning

---

**Version**: 1.0.0  
**Last Updated**: September 22, 2025  
**Maintainer**: FacePulse Development Team  
**License**: MIT License
