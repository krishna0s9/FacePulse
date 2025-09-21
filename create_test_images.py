#!/usr/bin/env python
"""
Create test images for face recognition training
This creates simple test images when camera access is not available
"""

import cv2
import numpy as np
import os


def create_test_images():
    """Create simple test images for demonstration"""

    # Create media/students directory if it doesn't exist
    media_dir = "media/students"
    os.makedirs(media_dir, exist_ok=True)

    print("Creating test images for face recognition training...")

    # Create a simple test image (you can replace this with actual photos)
    # For now, we'll create a placeholder image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    test_image[:] = (100, 100, 100)  # Gray background

    # Add some text to indicate it's a test image
    cv2.putText(test_image, 'TEST IMAGE', (200, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(test_image, 'Replace with actual photos', (150, 280),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Save test images
    test_images = [
        "STU001_John_Doe.jpg",
        "STU002_Jane_Smith.jpg",
        "STU003_Mike_Johnson.jpg"
    ]

    for filename in test_images:
        filepath = os.path.join(media_dir, filename)
        cv2.imwrite(filepath, test_image)
        print(f"✓ Created test image: {filename}")

    print(f"\nTest images created in {media_dir}/")
    print("Note: These are placeholder images. Replace them with actual student photos for real face recognition.")
    print("For real testing, you can:")
    print("1. Take photos with your phone")
    print("2. Save them in media/students/ with naming: STU001_YourName.jpg")
    print("3. Then run: python manage.py load_encodings")


if __name__ == "__main__":
    create_test_images()
