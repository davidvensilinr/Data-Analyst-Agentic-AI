#!/usr/bin/env python3
"""
Main entry point for the Autonomous Data Analyst Backend.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.api.main import app
from config.settings import settings


def create_directories():
    """Create necessary directories."""
    directories = [
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
        "./data",
        "./logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    """Main entry point."""
    # Create necessary directories
    create_directories()
    
    # Print startup information
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 Server will be available at: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🤖 Mock LLM Mode: {settings.MOCK_LLM_MODE}")
    print(f"📊 Database: {settings.DATABASE_URL}")
    
    # Run the application
    uvicorn.run(
        "app.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True
    )


if __name__ == "__main__":
    main()
