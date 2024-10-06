from starlette.config import Config
from dotenv import load_dotenv
import os

load_dotenv()
config = Config()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

if not MONGODB_URI or not MONGODB_DB:
    raise EnvironmentError("MongoDB environment variables are missing")

# Facebook API Configuration
FACEBOOK_API_VERSION = os.getenv("FACEBOOK_API_VERSION", default="19.0")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_USER_TOKEN = os.getenv("FACEBOOK_USER_TOKEN")

# Added validation for Facebook API keys
if not all([FACEBOOK_PAGE_ID, FACEBOOK_APP_SECRET, FACEBOOK_USER_TOKEN]):
    raise EnvironmentError("Facebook API credentials are missing")

# AWS API Configuration
AWS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Cognito Configuration
COGNITO_REGION = os.getenv('COGNITO_REGION')
COGNITO_POOL_ID = os.getenv('COGNITO_POOL_ID')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')
S3_BUCKET_NAME = config('S3_BUCKET_NAME')

# Gmail Configuration
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
