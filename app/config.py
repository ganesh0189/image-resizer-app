import os
import tempfile

class Config:
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Upload folder configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(tempfile.gettempdir(), 'image_resizer_uploads'))
    
    # File size limits
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB total upload limit
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file limit
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Debug mode - set to False in production
    DEBUG = os.environ.get('FLASK_ENV') != 'production'
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', '678bcbacb43b90dfa4e0962f9cf1535b66be277b3ffd66094988eb0b56d93e31')
    
    # Production settings
    TESTING = False
    PROPAGATE_EXCEPTIONS = True

# Create uploads directory if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
# Ensure proper permissions
os.chmod(Config.UPLOAD_FOLDER, 0o755) 