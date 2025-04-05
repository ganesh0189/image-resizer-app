from app import create_app
from app.config import Config
import os

app = create_app(Config)

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    # In production, we don't need to run the development server
    if os.environ.get('FLASK_ENV') == 'production':
        app.run()
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
