import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # A secret key is needed for session management (to keep users logged in)
    # Generate a random one for production! You can use: openssl rand -hex 16
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-for-dev')

    # The single login code for everyone
    EVENT_ACCESS_CODE = os.environ.get('EVENT_ACCESS_CODE', 'DEFAULT_CODE')

    # Supported languages
    LANGUAGES = ['en', 'pt']