"""
Flask Image Upload Application

A web application that allows users to upload and view images.
Supports multiple image formats with file validation and security measures.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, Response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
from typing import Union, Dict, Any
from flask import send_file, request, abort
import numpy as np
import cv2
import io

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Application Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Configure Flask app settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): The name of the file to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index() -> str:
    """
    Render the main page with the image upload form.
    
    Returns:
        str: Rendered HTML template for the index page
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file() -> Response:
    """
    Handle file upload requests and save uploaded images.
    
    Validates the uploaded file, saves it to the upload directory,
    and redirects to the image viewing page on success.
    
    Returns:
        Response: Redirects to index page on error or view page on success
    """
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('File uploaded successfully!')
        return redirect(url_for('view_image', filename=filename))
    else:
        flash('Invalid file type. Please upload an image file.')
        return redirect(url_for('index'))

@app.route('/view/<filename>')
def view_image(filename: str) -> str:
    """
    Display the uploaded image in a viewing template.
    
    Args:
        filename (str): The name of the uploaded file to display
        
    Returns:
        str: Rendered HTML template for viewing the image
    """
    return render_template('view.html', filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename: str) -> Response:
    """
    Serve uploaded files from the upload directory.
    
    Args:
        filename (str): The name of the file to serve
        
    Returns:
        Response: The file content as a Flask response
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health')
def health_check() -> Dict[str, str]:
    """
    Provide a health check endpoint for monitoring the application status.
    
    Returns:
        Dict[str, str]: JSON response containing status and message
    """
    return {'status': 'healthy', 'message': 'Flask app is running'}

@app.route('/image/transform/grayscale', methods=['POST'])
def convert_to_gray_scale():  
    """
    Convert an uploaded image to grayscale and return the result.
    Expects a file upload (multipart/form-data) with key 'file'.
    Returns the grayscale image as a response.
    """

    # Check if the user actually sent a file with their request
    if 'file' not in request.files:  
        abort(400, description="No file part in the request") 

    # Get the file from the request
    file = request.files['file']  

    # Check if the file has a name (i.e., if a file was selected)
    if file.filename == '':  
        abort(400, description="No file selected")  
    
    # Check if the file exists and is an allowed image type
    if file and allowed_file(file.filename):  

        # Create a place in memory to temporarily store the file
        in_memory_file = io.BytesIO()  
        # Save the uploaded file into this memory space
        file.save(in_memory_file)  

        # Read the file's bytes into a numpy array
        data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)  

        # Decode the numpy array into an image using OpenCV
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)  

        # Check if the image was loaded correctly
        if img is None:  
            abort(400, description="Invalid image file")  

        # Convert the image to grayscale using OpenCV
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  

        # Encode the grayscale image as a PNG file in memory
        is_success, image_buffer = cv2.imencode(".png", gray)  

        # Check if the encoding worked
        if not is_success:  
            abort(500, description="Failed to encode image") 

         # Send the grayscale image back to the user as a response
        return send_file( 
            io.BytesIO(image_buffer.tobytes()),  # The image data in memory
            mimetype='image/png',  # Tell the browser this is a PNG image
            as_attachment=False,  # Show the image in the browser instead of downloading it
            download_name='grayscale.png'  # Name the file "grayscale.png" if downloaded
        )
    else:  
        abort(400, description="Invalid file type")  

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
