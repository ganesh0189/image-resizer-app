# Image Resizer and PDF Converter

A Flask-based web application that allows users to resize images and convert multiple images to PDF.

## Features

- Image Resizing
  - Upload single or multiple images
  - Specify custom dimensions
  - Maintain aspect ratio
  - Support for various image formats (JPG, PNG, etc.)
  - Download resized images

- PDF Conversion
  - Convert multiple images to PDF
  - Drag and drop interface
  - Reorder images before conversion
  - Custom PDF name
  - Download converted PDF

## Setup

1. Clone the repository:
```bash
git clone https://github.com/ganesh0189/image-resizer-app.git
cd image-resizer-app
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Technologies Used

- Python
- Flask
- HTML/CSS/JavaScript
- Pillow (Python Imaging Library)
- img2pdf

## License

MIT License 