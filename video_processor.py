import os
import cv2
import numpy as np
from pytubefix import YouTube
import tempfile
import logging
from fpdf import FPDF
import urllib.parse
import re

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logging.info(f"Temporary directory created: {self.temp_dir}")
    
    def validate_youtube_url(self, url):
        """Validate if the URL is a valid YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
    
    def download_video(self, youtube_url, update_callback):
        """Download YouTube video"""
        update_callback('downloading', 10, 'Downloading video from YouTube...')
        
        if not self.validate_youtube_url(youtube_url):
            raise ValueError("Invalid YouTube URL format")
        
        try:
            # Create YouTube object using pytubefix
            yt = YouTube(youtube_url)
            
            logging.info(f"Video title: {yt.title}")
            
            # Try multiple stream options in order of preference
            stream = None
            
            # First try: Progressive streams (video + audio together)
            progressive_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
            if progressive_streams:
                stream = progressive_streams.first()
                if stream:
                    logging.info(f"Using progressive stream: {stream.resolution}")
            
            # Second try: Adaptive video streams (video only)
            if not stream:
                adaptive_streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()
                if adaptive_streams:
                    stream = adaptive_streams.first()
                    if stream:
                        logging.info(f"Using adaptive video stream: {stream.resolution}")
            
            # Third try: Any mp4 stream
            if not stream:
                any_streams = yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
                if any_streams:
                    stream = any_streams.first()
                    if stream:
                        logging.info(f"Using fallback stream: {stream.resolution}")
            
            # Fourth try: Any video stream
            if not stream:
                video_streams = yt.streams.filter(only_video=True).order_by('resolution').desc()
                if video_streams:
                    stream = video_streams.first()
                    if stream:
                        logging.info(f"Using any video stream: {stream.resolution}")
            
            if not stream:
                raise ValueError("No suitable video stream found. This video may be restricted or unavailable.")
            
            video_path = os.path.join(self.temp_dir, 'video.mp4')
            
            # Download with error handling
            try:
                stream.download(output_path=self.temp_dir, filename='video.mp4')
            except Exception as download_error:
                logging.error(f"Download failed: {str(download_error)}")
                raise ValueError(f"Failed to download video stream: {str(download_error)}")
            
            # Verify file was downloaded
            if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
                raise ValueError("Downloaded video file is empty or missing")
            
            update_callback('downloading', 30, 'Video downloaded successfully')
            return video_path
            
        except Exception as e:
            logging.error(f"Error downloading video: {str(e)}")
            if "HTTP Error 400" in str(e):
                raise ValueError("YouTube blocked the download request. This video may be age-restricted, private, or have download restrictions.")
            elif "HTTP Error 403" in str(e):
                raise ValueError("Access to this video is forbidden. The video may be private or restricted.")
            elif "HTTP Error 404" in str(e):
                raise ValueError("Video not found. Please check the URL and try again.")
            else:
                raise ValueError(f"Failed to download video: {str(e)}")
    
    def extract_frames(self, video_path, update_callback):
        """Extract frames from video at regular intervals"""
        update_callback('extracting', 40, 'Extracting frames from video...')
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        logging.info(f"Video duration: {duration:.2f} seconds, FPS: {fps}, Total frames: {frame_count}")
        
        frames = []
        frame_interval = max(1, int(fps * 2))  # Extract one frame every 2 seconds
        
        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % frame_interval == 0:
                frames.append((frame_number, frame))
            
            frame_number += 1
            
            # Update progress
            progress = 40 + int((frame_number / frame_count) * 20)
            update_callback('extracting', progress, f'Extracted {len(frames)} frames...')
        
        cap.release()
        logging.info(f"Extracted {len(frames)} frames")
        return frames
    
    def detect_unique_slides(self, frames, update_callback):
        """Detect unique slides by comparing frames"""
        update_callback('analyzing', 60, 'Analyzing frames to detect unique slides...')
        
        if not frames:
            return []
        
        unique_slides = []
        similarity_threshold = 0.85  # Adjust this value to fine-tune slide detection
        
        for i, (frame_num, frame) in enumerate(frames):
            is_unique = True
            
            # Convert frame to grayscale for comparison
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Compare with existing unique slides
            for _, existing_gray in unique_slides:
                similarity = self.calculate_frame_similarity(gray_frame, existing_gray)
                if similarity > similarity_threshold:
                    is_unique = False
                    break
            
            if is_unique:
                unique_slides.append((frame, gray_frame))
                logging.info(f"Found unique slide at frame {frame_num}")
            
            # Update progress
            progress = 60 + int((i / len(frames)) * 20)
            update_callback('analyzing', progress, f'Found {len(unique_slides)} unique slides...')
        
        logging.info(f"Detected {len(unique_slides)} unique slides")
        return [slide[0] for slide in unique_slides]  # Return only the color frames
    
    def calculate_frame_similarity(self, frame1, frame2):
        """Calculate similarity between two grayscale frames using histogram comparison"""
        # Resize frames to same size if different
        if frame1.shape != frame2.shape:
            height = min(frame1.shape[0], frame2.shape[0])
            width = min(frame1.shape[1], frame2.shape[1])
            frame1 = cv2.resize(frame1, (width, height))
            frame2 = cv2.resize(frame2, (width, height))
        
        # Calculate histograms
        hist1 = cv2.calcHist([frame1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([frame2], [0], None, [256], [0, 256])
        
        # Compare histograms using correlation
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return similarity
    
    def generate_pdf(self, slides, update_callback):
        """Generate PDF from slide images"""
        update_callback('generating', 80, 'Generating PDF...')
        
        if not slides:
            raise ValueError("No slides to generate PDF")
        
        # Create PDF
        pdf = FPDF()
        
        for i, slide in enumerate(slides):
            # Save slide as temporary image
            temp_img_path = os.path.join(self.temp_dir, f'slide_{i}.jpg')
            cv2.imwrite(temp_img_path, slide)
            
            # Add page to PDF
            pdf.add_page()
            
            # Get image dimensions and scale to fit page
            img_height, img_width = slide.shape[:2]
            
            # A4 page dimensions in mm (210 x 297)
            page_width = 210
            page_height = 297
            margin = 10
            
            # Calculate scaling to fit image on page with margins
            scale_width = (page_width - 2 * margin) / (img_width * 0.264583)  # Convert pixels to mm
            scale_height = (page_height - 2 * margin) / (img_height * 0.264583)
            scale = min(scale_width, scale_height)
            
            # Calculate centered position
            scaled_width = img_width * 0.264583 * scale
            scaled_height = img_height * 0.264583 * scale
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            pdf.image(temp_img_path, x, y, scaled_width, scaled_height)
            
            # Clean up temporary image
            os.remove(temp_img_path)
            
            # Update progress
            progress = 80 + int((i / len(slides)) * 15)
            update_callback('generating', progress, f'Added slide {i+1}/{len(slides)} to PDF...')
        
        # Save PDF
        pdf_path = os.path.join(self.temp_dir, 'youtube_slides.pdf')
        pdf.output(pdf_path)
        
        update_callback('generating', 95, 'PDF generated successfully!')
        logging.info(f"PDF saved to: {pdf_path}")
        return pdf_path
    
    def process_video(self, youtube_url, update_callback):
        """Main processing pipeline"""
        try:
            # Download video
            video_path = self.download_video(youtube_url, update_callback)
            
            # Extract frames
            frames = self.extract_frames(video_path, update_callback)
            
            # Detect unique slides
            unique_slides = self.detect_unique_slides(frames, update_callback)
            
            if not unique_slides:
                raise ValueError("No unique slides detected in the video")
            
            # Generate PDF
            pdf_path = self.generate_pdf(unique_slides, update_callback)
            
            update_callback('completed', 100, f'Successfully generated PDF with {len(unique_slides)} slides!')
            return pdf_path
            
        except Exception as e:
            logging.error(f"Error in processing pipeline: {str(e)}")
            raise
