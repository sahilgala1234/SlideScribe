# YouTube Slide Extractor

## Overview

YouTube Slide Extractor is a Flask-based web application that downloads YouTube videos and extracts individual slides/frames to generate downloadable PDF documents. The application provides a user-friendly web interface for inputting YouTube URLs and tracks processing progress in real-time through background processing with status updates.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Framework**: Traditional server-side rendered HTML templates using Flask's Jinja2 templating engine
- **UI Framework**: Bootstrap 5 with dark theme for responsive design and consistent styling
- **Client-side Processing**: Vanilla JavaScript for form validation, real-time URL validation, and dynamic UI updates
- **Real-time Updates**: Client-side polling mechanism to track background processing status
- **Styling**: Custom CSS with Bootstrap overrides for processing animations and hover effects

### Backend Architecture
- **Web Framework**: Flask with Python for HTTP request handling and routing
- **Session Management**: Flask sessions with configurable secret key for tracking user processing tasks
- **Background Processing**: Python threading for non-blocking video processing operations
- **Status Tracking**: In-memory dictionary (`processing_status`) to store processing progress and status updates
- **Video Processing**: Custom `VideoProcessor` class handling YouTube video download and frame extraction
- **File Management**: Temporary file system storage for downloaded videos and generated PDFs

### Core Processing Pipeline
- **Video Download**: pytube library for YouTube video acquisition with progressive/adaptive stream fallback
- **Frame Extraction**: OpenCV (cv2) for video frame analysis and slide detection
- **PDF Generation**: FPDF library for creating downloadable PDF documents from extracted frames
- **Progress Callbacks**: Callback-based progress reporting system for real-time status updates

### Data Storage Solutions
- **Temporary Storage**: File system-based temporary directories for video and PDF files
- **Session Storage**: Flask sessions for tracking user-specific processing tasks
- **In-Memory Storage**: Python dictionaries for processing status and progress tracking
- **No Persistent Database**: Application operates without permanent data storage

### Authentication and Authorization
- **No Authentication**: Open access application without user accounts or login requirements
- **Session-based Tracking**: UUID-based session identification for processing task isolation
- **No Authorization**: All features available to all users without restrictions

## External Dependencies

### Core Libraries
- **Flask**: Web framework for HTTP routing and template rendering
- **pytube**: YouTube video downloading and metadata extraction
- **OpenCV (cv2)**: Computer vision library for video processing and frame analysis
- **FPDF**: PDF generation library for creating downloadable documents
- **NumPy**: Numerical computing support for image processing operations

### Frontend Dependencies
- **Bootstrap 5**: CSS framework via CDN for responsive UI components
- **Font Awesome 6**: Icon library via CDN for visual indicators and buttons
- **Replit Bootstrap Theme**: Dark theme variant for consistent styling

### Development and Deployment
- **Werkzeug**: WSGI utilities including ProxyFix middleware for proper header handling
- **Python Standard Library**: tempfile, threading, uuid, logging, os, urllib, re modules
- **No Database Dependencies**: Application operates without external database connections
- **No External APIs**: Beyond YouTube video access through pytube library

### Infrastructure Requirements
- **Python 3.x Runtime**: Required for Flask application execution
- **File System Access**: Temporary directory creation and file I/O operations
- **Network Access**: Required for YouTube video downloading and CDN resource loading
- **Threading Support**: Background processing requires thread-safe operations
