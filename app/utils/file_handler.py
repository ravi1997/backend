import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid
from datetime import datetime, timezone
import puremagic as magic  # pure-python library for file type detection (no libmagic needed)

# Configure upload settings
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_mimetype(filepath):
    """Get the actual MIME type of a file"""
    try:
        return magic.from_file(filepath, mime=True)
    except:
        return None

def save_uploaded_file(file, form_id, question_id):
    """Save an uploaded file and return the file info"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed: {file.filename}")
    
    # Generate a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Create directory structure: uploads/<form_id>/<question_id>/
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 
                              str(form_id), str(question_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    filepath = os.path.join(upload_dir, unique_filename)
    
    # Check file size before saving
    file.seek(0, os.SEEK_END)  # Go to end of file
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
    
    # Save the file
    file.save(filepath)
    
    # Get the actual MIME type of the saved file
    actual_mimetype = get_file_mimetype(filepath)
    
    # Return file info that will be stored in the database
    return {
        'original_filename': filename,
        'stored_filename': unique_filename,
        'filepath': filepath,
        'mimetype': actual_mimetype or file.content_type,
        'size': file_size,
        'upload_date': datetime.now(timezone.utc)
    }

def get_file_url(file_info, form_id, question_id):
    """Generate a URL for accessing the stored file"""
    return f"/form/api/v1/form/{form_id}/files/{question_id}/{file_info['stored_filename']}"

def delete_file(file_path):
    """Delete a file from the filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # Remove empty directories up to the question level
            dir_path = os.path.dirname(file_path)
            try:
                if not os.listdir(dir_path):  # If directory is empty
                    os.rmdir(dir_path)
                    # Also try to remove the parent form directory if it's empty
                    parent_dir = os.path.dirname(dir_path)
                    if not os.listdir(parent_dir):  # If parent is also empty
                        os.rmdir(parent_dir)
            except OSError:
                # Directory not empty, which is fine
                pass
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False