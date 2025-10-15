from flask import request, jsonify, send_file, render_template
import os
import logging
from app.processing import extract_data
from app import app
import shutil
import threading
import time
from typing import Set

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global download directory - use absolute path
DOWNLOAD_DIRECTORY = '/app/download'

# Track files that should be deleted after download
files_to_cleanup: Set[str] = set()

def clean_download_directory():
    """Deletes the entire download directory and recreates it."""
    try:
        if os.path.exists(DOWNLOAD_DIRECTORY):
            shutil.rmtree(DOWNLOAD_DIRECTORY)
            logger.info(f"Deleted entire directory: {DOWNLOAD_DIRECTORY}")

        os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
        logger.info(f"Recreated directory: {DOWNLOAD_DIRECTORY}")
        
        # Clear the cleanup tracking
        files_to_cleanup.clear()
    except Exception as e:
        logger.error(f"Error cleaning download directory: {str(e)}")
        raise

def schedule_file_cleanup(file_path: str, delay: int = 300):  # 5 minutes delay
    """Schedule a file for deletion after specified delay."""
    def cleanup():
        time.sleep(delay)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
                files_to_cleanup.discard(file_path)
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")
    
    # Add to tracking set
    files_to_cleanup.add(file_path)
    
    # Start cleanup thread
    thread = threading.Thread(target=cleanup)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    """Render the main page."""
    logger.info("Rendering index.html")
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_data():
    """Process climate data extraction request."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        country = data.get('country')
        variable = data.get('variable')
        method = data.get('method')
        area = data.get('area')

        # Validate required parameters
        if not all([country, variable, method, area]):
            return jsonify({'error': 'Country, variable, method, and area are required!'}), 400

        logger.info(f"Processing request: country={country}, variable={variable}, method={method}, area={area}")

        # Clean download directory before processing
        clean_download_directory()

        # Determine if subregions should be used
        subregions = (area == "subregion")

        # Extract data
        output_path = extract_data(country, variable, method, subregions=subregions)

        # Return the download link
        filename = os.path.basename(output_path)
        download_url = f'/download/{filename}'
        
        logger.info(f"Processing completed successfully. Download URL: {download_url}")
        return jsonify({'download_link': download_url}), 200

    except ValueError as e:
        logger.error(f"Value error in process_data: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError as e:
        logger.error(f"File not found in process_data: {str(e)}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error in process_data: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download processed files and schedule cleanup."""
    try:
        # Security: Basic filename validation
        if '..' in filename or filename.startswith('/'):
            return jsonify({'error': 'Invalid filename'}), 400

        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        logger.info(f"Attempting to serve file: {file_path}")
        
        if os.path.exists(file_path):
            # Schedule cleanup after 5 minutes (adjust as needed)
            schedule_file_cleanup(file_path, delay=300)  # 5 minutes
            
            return send_file(file_path, as_attachment=True, 
                           as_attachment=True,
                           download_name=filename)
        else:
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found!'}), 404
            
    except Exception as e:
        logger.error(f"Error in download_file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual cleanup endpoint for testing."""
    try:
        clean_download_directory()
        return jsonify({'message': 'Download directory cleaned successfully'}), 200
    except Exception as e:
        logger.error(f"Error in manual cleanup: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker/load balancers."""
    cleanup_status = f"{len(files_to_cleanup)} files scheduled for cleanup"
    return jsonify({
        'status': 'healthy', 
        'message': 'Climate Data Extraction API is running',
        'domain': 'climatedata.indecol.no',
        'cleanup_status': cleanup_status
    })

# Ensure download directory exists when module is imported
os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)