# app/core/config.py

from starlette.config import Config
from dotenv import load_dotenv

load_dotenv()
config = Config()

# MongoDB Configuration
MONGODB_URI = config("MONGODB_URI")
MONGODB_DB = config("MONGODB_DB")

# Facebook API Configuration
FACEBOOK_API_VERSION = config("FACEBOOK_API_VERSION", default="19.0")
FACEBOOK_PAGE_ID = config("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = config("FACEBOOK_APP_SECRET")
FACEBOOK_USER_TOKEN = config("FACEBOOK_USER_TOKEN")

# AWS API Configuration
AWS_KEY_ID = config('aws_access_key_id')
AWS_SECRET_KEY = config('aws_secret_access_key')
REGION_NAME = config('region_name')

# Gemini API Configuration
GEMINI_API_KEY = config('GEMINI_API_KEY')

# Cognito Configuration
COGNITO_REGION = config('COGNITO_REGION')
COGNITO_POOL_ID = config('COGNITO_POOL_ID')
COGNITO_APP_CLIENT_ID = config('COGNITO_APP_CLIENT_ID')
S3_BUCKET_NAME = config('S3_BUCKET_NAME')