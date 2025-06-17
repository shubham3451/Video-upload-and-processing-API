import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "video_db")

REDIS_BROKER_URL = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
THUMBNAILS_DIR = os.getenv("THUMBNAILS_DIR", "thumbnails")

