import os
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import routes_bp
from app.status_routes import status_bp
from app.system_monitor import system_monitor

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
    
    # Register blueprints
    app.register_blueprint(routes_bp)
    app.register_blueprint(status_bp)
    
    # Start system monitoring
    system_monitor.start_monitoring()
    
    # Ensure the uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.chmod(app.config['UPLOAD_FOLDER'], 0o755)
    
    return app 