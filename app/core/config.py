# app/core/config.py

from starlette.config import Config

config = Config()

# MongoDB Configuration
MONGODB_URI = config("MONGODB_URI", default="mongodb://localhost:27017")
MONGODB_DB = config("MONGODB_DB", default="mydatabase")

# Facebook API Configuration
FACEBOOK_API_VERSION = config("FACEBOOK_API_VERSION", default="v13.0")
PAGE_ID = config("PAGE_ID", default="default")
ACCESS_TOKEN = config("ACCESS_TOKEN", default="default")
