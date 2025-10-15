FacePulse 🟢

FacePulse is a Face Recognition Attendance System built with Python and Django. It automates attendance by recognizing faces in real-time, removing the need for manual logging. Ideal for classrooms, offices, and events.


🔹 Features

Real-time face recognition for accurate attendance tracking.

Django backend with authentication & role-based authorization.

OpenCV integration for facial detection and recognition.

CSV export of attendance logs.

User-friendly web interface for administrators and staff.

Optional email notifications for absentee alerts.


🔹 Tech Stack

Frontend: HTML, CSS, JavaScript

Backend: Django (Python)

Libraries & Tools: OpenCV, NumPy, face_recognition, Pandas

Database: SQLite / PostgreSQL


🔹 Models Overview

1. User Model (extends Django User)

Stores credentials, email, and roles (Admin, Teacher, Student).

Handles authentication.



2. Profile Model

Stores profile photo, class/department, and facial encodings.



3. Attendance Model

Logs attendance entries with timestamp, user ID, and status.



4. Class/Group Model

Organizes students/employees for easier attendance management.



5. Authorization & Permissions

Role-based access:

Admin: Full access to manage users, classes, and attendance.

Teacher/Staff: Can mark and view attendance.

Student: Can view personal attendance only.


Secure operations using login-required views and permission decorators.



🔹 Installation & Setup

1. Clone the repository:



git clone https://github.com/krishna0s9/FacePulse.git
cd FacePulse

2. Create a virtual environment:



python -m venv venv
# Windows
venv\Scripts\activate

3. Install dependencies:



pip install -r requirements.txt

4. Run migrations:



python manage.py migrate

5. Create a superuser for admin access:



python manage.py createsuperuser

6. Start the server:



python manage.py runserver

7. Access the app:
Open http://127.0.0.1:8000/ in your browser.


🔹 Usage

1. Admin creates user accounts and assigns roles.


2. Add students/employees with facial images for recognition.


3. Use the webcam to scan faces in real-time.


4. Attendance is automatically logged with timestamps.


5. Export attendance as CSV for reporting.



🔹 Demo Video 🎥

Watch the demo here: https://youtu.be/FTBlYGflQgc?si=s25UN4teZJT4JWCM


🔹 Future Enhancements

Add SMS or Email notifications for absentees.

Implement multi-factor authentication (MFA).

Support multiple face recognition models for higher accuracy.

Deploy on cloud for remote access.
