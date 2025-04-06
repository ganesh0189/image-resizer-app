# Image Resizer and PDF Converter

A modern, user-friendly web application built with Flask that allows users to resize images and convert multiple images to PDF. The application features a clean, intuitive interface with responsive design and real-time preview capabilities.

![Application Screenshot](app/static/images/screenshot.png)

## 🌟 Features

### Image Resizing
- Upload single or multiple images with drag-and-drop support
- Specify custom dimensions while maintaining aspect ratio
- Support for various image formats (JPG, PNG, GIF, etc.)
- Real-time preview of resized images
- Batch processing for multiple images
- Instant download of resized images

### Image Compression
- Compress images to reduce file size
- Specify target file size or quality level
- Maintain image quality while reducing file size
- Real-time preview of compressed images
- Instant download of compressed images

### PDF Conversion
- Convert multiple images to a single PDF document
- Intuitive drag-and-drop interface for image upload
- Reorder images before conversion
- Custom PDF naming
- High-quality PDF output
- Instant download of converted PDF

### User Interface
- Modern, responsive design
- Intuitive navigation
- Step-by-step process flow
- About section with application information
- Creator details and contact information
- Clean and professional header section
- Transparent styling for a modern look

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ganesh0189/image-resizer-app.git
cd image-resizer-app
```

2. Create and activate a virtual environment:
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

5. Access the application:
```
http://localhost:8080
```

## 🛠️ Technologies Used

- **Backend:**
  - Python
  - Flask (Web Framework)
  - Pillow (Image Processing)
  - img2pdf (PDF Conversion)
  - psutil (System Monitoring)

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript
  - Modern UI/UX Design

## 🌐 Deployment

The application is deployed on Render and can be accessed at:
```
https://image-resizer-app.onrender.com
```

### Deployment Steps on Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
   - Environment: Python 3
4. Deploy the application

### Git Repository
The application is available on GitHub at:
```
https://github.com/ganesh0189/image-resizer-app
```

## 👨‍💻 Creator

**Ganesh Bollem**
- GitHub: [ganesh0189](https://github.com/ganesh0189)
- Email: ganeshbollem0189@gmail.com

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/ganesh0189/image-resizer-app/issues).

## 📞 Support

For support, please open an issue in the GitHub repository or contact the creator directly. 