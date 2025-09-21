#!/usr/bin/env python
"""
Test script for face recognition functionality
Run this script to test if face_recognition and opencv are working properly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facepulse.settings')
django.setup()


def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")

    try:
        import cv2
        print("✓ OpenCV imported successfully")
        print(f"  OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False

    try:
        import numpy as np
        print("✓ NumPy imported successfully")
        print(f"  NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False

    try:
        import face_recognition
        print("✓ face_recognition imported successfully")
    except ImportError as e:
        print(f"✗ face_recognition import failed: {e}")
        return False

    try:
        from PIL import Image
        print("✓ PIL imported successfully")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        return False

    return True


def test_camera():
    """Test if camera can be accessed"""
    print("\nTesting camera access...")

    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera is accessible and working")
                cap.release()
                return True
            else:
                print("✗ Camera opened but cannot read frames")
                cap.release()
                return False
        else:
            print("✗ Cannot open camera")
            return False
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def test_face_recognition():
    """Test face recognition with a simple example"""
    print("\nTesting face recognition...")

    try:
        import face_recognition
        import numpy as np

        # Create a simple test image (just a black image)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Try to find faces (should return empty list for black image)
        face_locations = face_recognition.face_locations(test_image)
        print(
            f"✓ face_recognition.face_locations() works (found {len(face_locations)} faces)")

        # Try to encode faces
        face_encodings = face_recognition.face_encodings(
            test_image, face_locations)
        print(
            f"✓ face_recognition.face_encodings() works (encoded {len(face_encodings)} faces)")

        return True
    except Exception as e:
        print(f"✗ Face recognition test failed: {e}")
        return False


def test_django_models():
    """Test Django models and database connection"""
    print("\nTesting Django models...")

    try:
        from attendance.models import Student, Attendance
        from django.conf import settings

        print(f"✓ Django models imported successfully")
        print(f"  Database: {settings.DATABASES['default']['ENGINE']}")

        # Test database connection
        student_count = Student.objects.count()
        attendance_count = Attendance.objects.count()

        print(f"✓ Database connection working")
        print(f"  Students in database: {student_count}")
        print(f"  Attendance records: {attendance_count}")

        return True
    except Exception as e:
        print(f"✗ Django models test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Face Recognition System Test")
    print("=" * 40)

    tests = [
        test_imports,
        test_camera,
        test_face_recognition,
        test_django_models
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed! Face recognition system is ready.")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
