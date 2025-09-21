#!/usr/bin/env python
"""
Script to capture training images for face recognition
This script will help you capture sample images of students for training the system
"""

import cv2
import os
import time


def capture_training_images():
    """Capture training images using webcam"""

    # Create media/students directory if it doesn't exist
    media_dir = "media/students"
    os.makedirs(media_dir, exist_ok=True)

    print("Face Recognition Training Image Capture")
    print("=" * 50)
    print("Instructions:")
    print("1. Position yourself in front of the camera")
    print("2. Press 'S' or 'SPACEBAR' to capture an image")
    print("3. Press 'Q' or 'ESC' to quit")
    print("4. Images will be saved as: STU001_YourName.jpg, STU002_YourName.jpg, etc.")
    print("=" * 50)

    # Initialize camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    try:
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Load face cascade for face detection
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        image_count = 0
        student_name = input("Enter your name (for filename): ").strip()
        if not student_name:
            student_name = "Student"

        print(f"\nReady to capture images for {student_name}")
        print("Press 'S' or 'SPACEBAR' to capture, 'Q' or 'ESC' to quit")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, 'Face Detected', (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Add instructions
            cv2.putText(frame, 'Press S/SPACE to capture, Q/ESC to quit', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f'Captured: {image_count}', (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Display frame
            cv2.imshow('Training Image Capture', frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF

            # Space bar or 'S' to capture
            if key == ord(' ') or key == ord('s') or key == ord('S'):
                if len(faces) > 0:
                    image_count += 1
                    filename = f"STU{image_count:03d}_{student_name}.jpg"
                    filepath = os.path.join(media_dir, filename)

                    # Save the image
                    cv2.imwrite(filepath, frame)
                    print(f"✓ Captured image {image_count}: {filename}")

                    # Show confirmation
                    cv2.putText(frame, f'SAVED: {filename}', (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow('Training Image Capture', frame)
                    cv2.waitKey(1000)  # Show confirmation for 1 second
                else:
                    print(
                        "No face detected! Please position yourself in front of the camera.")

            elif key == ord('q') or key == ord('Q') or key == 27:  # 'Q' or ESC to quit
                print("Quitting...")
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup - ensure all windows are properly closed
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Wait for window to close

        print(
            f"\nCapture complete! {image_count} images saved to {media_dir}/")
        print("Next steps:")
        print("1. Run: python manage.py load_encodings")
        print("2. Start Django server: python manage.py runserver")
        print("3. Test at: http://127.0.0.1:8000/attendance/take/")


if __name__ == "__main__":
    capture_training_images()
