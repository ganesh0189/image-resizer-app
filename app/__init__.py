import os
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import init_routes

def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static'))
    CORS(app)
    
    # Configure app
    app.config.from_object(config_class)
    
    # Set production settings
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Initialize routes and error handlers
    init_routes(app)
    
    # Ensure the uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.chmod(app.config['UPLOAD_FOLDER'], 0o755)
    
    return app 