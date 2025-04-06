from flask import request, send_file, Blueprint, jsonify, render_template, url_for, current_app
import os
import json
import img2pdf
from app.utils import resize_image, compress_image
from werkzeug.utils import secure_filename
import time

routes_bp = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes_bp.route('/')
def index():
    return render_template('index.html')

@routes_bp.route('/resize')
def resize_page():
    return render_template('resize.html')

@routes_bp.route('/compress')
def compress_page():
    return render_template('compress.html')

@routes_bp.route('/pdf')
def pdf_page():
    return render_template('pdf.html')

@routes_bp.route('/resize', methods=['POST'])
def resize():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        width = int(request.form['width'])
        height = int(request.form['height'])
        if width <= 0 or height <= 0:
            return jsonify({"error": "Width and height must be positive numbers"}), 400
    except ValueError:
        return jsonify({"error": "Invalid width or height"}), 400

    maintain_aspect_ratio = request.form.get('maintain_aspect_ratio', 'true').lower() == 'true'

    filename = secure_filename(file.filename)
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    try:
        # Get original file size
        original_size = os.path.getsize(input_path)
        
        # Resize the image
        output_path = resize_image(input_path, width, height, maintain_aspect_ratio, current_app.config['UPLOAD_FOLDER'])
        
        # Get new file size
        new_size = os.path.getsize(output_path)
        
        # Calculate reduction percentage
        reduction = round((1 - (new_size / original_size)) * 100, 2)
        
        # Get the basename of the output file (it already has the resized_ prefix from resize_image)
        result_filename = os.path.basename(output_path)
        
        # Return JSON with file details
        return jsonify({
            "preview_url": url_for('routes.get_image', filename=result_filename),
            "download_url": url_for('routes.download_image', filename=result_filename),
            "original_size": original_size,
            "new_size": new_size,
            "reduction": reduction
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)

@routes_bp.route('/compress', methods=['POST'])
def compress():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        try:
            target_size_kb = int(request.form.get('target_size_kb', 0))
            if target_size_kb <= 0:
                return jsonify({"error": "Target size must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid target size"}), 400

        user_quality = request.form.get('quality')
        if user_quality:
            try:
                user_quality = int(user_quality)
                if not 1 <= user_quality <= 100:
                    return jsonify({"error": "Quality must be between 1 and 100"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid quality value"}), 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        try:
            # Get original file size
            original_size = os.path.getsize(input_path)
            
            # Compress the image
            output_path = compress_image(input_path, target_size_kb, user_quality, current_app.config['UPLOAD_FOLDER'])
            
            # Get new file size
            new_size = os.path.getsize(output_path)
            
            # Calculate reduction percentage
            reduction = round((1 - (new_size / original_size)) * 100, 2)
            
            # Get the basename of the output file
            result_filename = os.path.basename(output_path)
            
            # Return JSON with file details
            return jsonify({
                "preview_url": url_for('routes.get_image', filename=result_filename),
                "download_url": url_for('routes.download_image', filename=result_filename),
                "original_size": original_size,
                "new_size": new_size,
                "reduction": reduction
            })
        except Exception as e:
            current_app.logger.error(f"Error processing image: {str(e)}")
            return jsonify({"error": "Error processing image"}), 500
        finally:
            # Clean up input file
            if os.path.exists(input_path):
                os.remove(input_path)
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@routes_bp.route('/image/<filename>')
def get_image(filename):
    try:
        # Get the file path
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "Image not found"}), 404
            
        # Get the file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # Set the correct MIME type based on file extension
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        # Send the file with proper headers
        response = send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=False
        )
        
        # Add cache control headers
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return jsonify({"error": "Error serving image"}), 500

@routes_bp.route('/download/<filename>')
def download_image(filename):
    return send_file(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@routes_bp.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files selected"}), 400
    
    # Validate files
    for file in files:
        if not allowed_file(file.filename):
            return jsonify({"error": f"Invalid file type: {file.filename}"}), 400
        if file.content_length > current_app.config['MAX_FILE_SIZE']:
            return jsonify({"error": f"File too large: {file.filename}"}), 413
    
    try:
        # Get PDF name from form or generate one
        pdf_name = request.form.get('pdf_name', 'converted_images')
        if not pdf_name.endswith('.pdf'):
            pdf_name += '.pdf'
        
        # Create a temporary directory for images
        temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_pdf')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save all images
        image_paths = []
        for i, file in enumerate(files):
            filename = secure_filename(f"image_{i}_{file.filename}")
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            image_paths.append(file_path)
        
        # Convert images to PDF
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_name)
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        
        # Clean up temporary files
        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        return jsonify({
            "success": True,
            "filename": pdf_name,
            "download_url": url_for('routes.download_pdf', filename=pdf_name),
            "file_size": file_size,
            "page_count": len(files)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/download-pdf/<filename>')
def download_pdf(filename):
    return send_file(
        os.path.join(current_app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True,
        download_name=filename
    )

def init_routes(app):
    app.register_blueprint(routes_bp)
    
    @app.errorhandler(413)
    def request_entity_too_large(e):
        """Handle request entity too large error."""
        if request.path == '/convert-to-pdf':
            # Check if the request has a content length
            content_length = request.content_length
            if content_length and content_length > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({
                    'error': 'Total file size exceeds limit'
                }), 413
            return jsonify({
                'error': 'Individual file size exceeds limit'
            }), 413
        else:
            return jsonify({
                'error': 'File size exceeds limit'
            }), 413

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        return jsonify({"error": str(error)}), 500
