from PIL import Image
import os
import io
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    """Get the size of a file-like object."""
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset position
    return size

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def resize_image(input_path, width, height, maintain_aspect_ratio=True, upload_folder="uploads"):
    with Image.open(input_path) as img:
        if maintain_aspect_ratio:
            img.thumbnail((width, height), Image.LANCZOS)
        else:
            img = img.resize((width, height), Image.LANCZOS)

        output_path = os.path.join(upload_folder, f"resized_{os.path.basename(input_path)}")
        img.save(output_path)
        return output_path

def compress_image(input_path, target_size_kb, user_quality=None, upload_folder="uploads"):
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img_format = "JPEG"
            low, high = 10, 95
            best_quality = high if user_quality is None else user_quality
            best_bytes = None

            original_size_kb = os.path.getsize(input_path) / 1024
            
            # Always create a new file, even if the original is already smaller
            if user_quality is not None:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=img_format, quality=user_quality)
                output_path = os.path.join(upload_folder, f"compressed_{os.path.splitext(os.path.basename(input_path))[0]}.jpg")
                with open(output_path, "wb") as f:
                    f.write(img_bytes.getvalue())
                return output_path

            # If no user quality specified, find the best quality that meets the target size
            while low <= high:
                mid = (low + high) // 2
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=img_format, quality=mid)
                size_kb = len(img_bytes.getvalue()) / 1024

                if size_kb <= target_size_kb:
                    best_quality = mid
                    best_bytes = img_bytes.getvalue()
                    high = mid - 1
                else:
                    low = mid + 1

            output_path = os.path.join(upload_folder, f"compressed_{os.path.splitext(os.path.basename(input_path))[0]}.jpg")
            with open(output_path, "wb") as f:
                f.write(best_bytes if best_bytes else img_bytes.getvalue())
            return output_path
    except Exception as e:
        import traceback
        print(f"Error in compress_image: {str(e)}")
        print(traceback.format_exc())
        raise

def validate_file(file, max_size):
    """Validate a single file."""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, "Invalid file type"
    
    size = get_file_size(file)
    if size > max_size:
        return False, "File size exceeds limit"
    
    return True, None

def save_file(file, upload_folder):
    """Save a file to the upload folder and return the path."""
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath

def cleanup_files(files):
    """Clean up temporary files."""
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception:
            pass  # Ignore cleanup errors
