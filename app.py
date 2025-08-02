import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix
from video_processor import VideoProcessor
import tempfile
import threading
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Global dictionary to store processing status
processing_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    youtube_url = request.form.get('youtube_url', '').strip()
    
    if not youtube_url:
        flash('Please enter a YouTube URL', 'error')
        return redirect(url_for('index'))
    
    # Generate unique session ID for this processing task
    session_id = str(uuid.uuid4())
    session['processing_id'] = session_id
    
    # Initialize processing status
    processing_status[session_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing...',
        'error': None,
        'pdf_path': None
    }
    
    # Start processing in background thread
    thread = threading.Thread(target=process_video_background, args=(youtube_url, session_id))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('processing'))

def process_video_background(youtube_url, session_id):
    """Background task to process video and generate PDF"""
    try:
        processor = VideoProcessor()
        
        # Update status callback
        def update_status(status, progress, message):
            processing_status[session_id] = {
                'status': status,
                'progress': progress,
                'message': message,
                'error': None,
                'pdf_path': processing_status[session_id].get('pdf_path')
            }
        
        # Process video and generate PDF
        pdf_path = processor.process_video(youtube_url, update_status)
        
        # Update final status
        processing_status[session_id] = {
            'status': 'completed',
            'progress': 100,
            'message': 'PDF generated successfully!',
            'error': None,
            'pdf_path': pdf_path
        }
        
    except Exception as e:
        logging.error(f"Error processing video: {str(e)}")
        processing_status[session_id] = {
            'status': 'error',
            'progress': 0,
            'message': 'Processing failed',
            'error': str(e),
            'pdf_path': None
        }

@app.route('/processing')
def processing():
    processing_id = session.get('processing_id')
    if not processing_id or processing_id not in processing_status:
        flash('No processing session found', 'error')
        return redirect(url_for('index'))
    
    return render_template('processing.html', processing_id=processing_id)

@app.route('/status/<processing_id>')
def get_status(processing_id):
    """API endpoint to get processing status"""
    if processing_id not in processing_status:
        return jsonify({'error': 'Invalid processing ID'}), 404
    
    return jsonify(processing_status[processing_id])

@app.route('/download/<processing_id>')
def download_pdf(processing_id):
    """Download the generated PDF"""
    if processing_id not in processing_status:
        flash('Invalid processing session', 'error')
        return redirect(url_for('index'))
    
    status = processing_status[processing_id]
    if status['status'] != 'completed' or not status['pdf_path']:
        flash('PDF not ready for download', 'error')
        return redirect(url_for('processing'))
    
    try:
        return send_file(
            status['pdf_path'],
            as_attachment=True,
            download_name='youtube_slides.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        logging.error(f"Error downloading PDF: {str(e)}")
        flash('Error downloading PDF', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
