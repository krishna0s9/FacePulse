# Student Images Directory

Place student images in this directory with the following naming convention:

## Naming Format
`roll_no_name.jpg`

## Examples
- `001_John_Doe.jpg`
- `002_Jane_Smith.jpg`
- `003_Mike_Johnson.jpg`

## Requirements
- Clear, front-facing photos
- Good lighting
- Single person per image
- Supported formats: JPG, JPEG, PNG, BMP, TIFF

## Usage
After placing images here, run:
```bash
python manage.py load_encodings
```

This will extract face encodings and store them in the database for face recognition.
