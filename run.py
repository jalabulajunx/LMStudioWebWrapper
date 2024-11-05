# run.py
import os
from dotenv import load_dotenv
from server import create_app, socketio
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    logger.info("Starting application initialization...")

    # Create application instance
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    if __name__ == '__main__':
        logger.info("Starting server...")
        # Get port from environment or default to 5000
        port = int(os.getenv('PORT', 5000))

        # Run the application with minimal settings first
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=False  # Disable reloader temporarily
        )
except Exception as e:
    logger.error(f"Error starting server: {str(e)}", exc_info=True)
