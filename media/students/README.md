# Student Images Directory

This directory contains student images for face recognition training.

## File Naming Convention

Place student images in this directory with the following naming convention:
- `ROLL_NO_NAME.jpg` (e.g., `STU001_John_Doe.jpg`)
- `ROLL_NO_NAME.png` (e.g., `STU002_Jane_Smith.png`)

## Supported Formats

- JPG/JPEG
- PNG
- BMP
- TIFF

## Usage

1. Add student images to this directory following the naming convention
2. Run the management command to extract face encodings:
   ```bash
   python manage.py load_encodings
   ```
3. Use the face recognition attendance system

## Notes

- Each image should contain exactly one face
- Images with multiple faces will use the first detected face
- Images without faces will be skipped
- Good lighting and clear face visibility improve recognition accuracy
