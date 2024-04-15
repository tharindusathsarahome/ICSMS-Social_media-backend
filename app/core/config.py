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
