from celery import Celery
from .config import REDIS_BROKER_URL, GCS_BUCKET_NAME, THUMBNAILS_DIR
from .service import get_video_duration, generate_thumbnail
from .gcs import upload_file_to_gcs
from bson import ObjectId
import os
from google.cloud import storage
from pymongo import MongoClient
from .config import MONGODB_URI, MONGODB_DB


celery_app = Celery("worker", broker=REDIS_BROKER_URL)

@celery_app.task(name="app.celery.process_video")
def process_video(video_id: str, video_gcs_path: str, filename: str):
    """
    Background task to process video:
    - Download video from GCS to temp
    - Extract duration
    - Generate thumbnail at 10% duration
    - Upload thumbnail to GCS
    - Update MongoDB record
    """
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    videos_collection = db["videos"]
    tmp_dir = "/tmp/video_processing"
    os.makedirs(tmp_dir, exist_ok=True)
    local_video_path = os.path.join(tmp_dir, filename)
    local_thumbnail_path = None

    try:
        # Download video from GCS
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(video_gcs_path)
        blob.download_to_filename(local_video_path)

        # Update status to 'processing'
        videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"status": "processing"}}
        )

        # Get duration
        duration_seconds = get_video_duration(local_video_path)
        duration_str = f"{int(duration_seconds // 3600):02}:{int((duration_seconds % 3600) // 60):02}:{int(duration_seconds % 60):02}"

        # Generate thumbnail
        thumbnail_time = duration_seconds * 0.1
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        thumbnail_filename = f"{video_id}.jpg"
        local_thumbnail_path = os.path.join(THUMBNAILS_DIR, thumbnail_filename)

        generate_thumbnail(local_video_path, local_thumbnail_path, thumbnail_time)

        # Upload thumbnail to GCS
        thumbnail_gcs_path = f"thumbnails/{thumbnail_filename}"
        thumbnail_url = upload_file_to_gcs(local_thumbnail_path, thumbnail_gcs_path)

        # Update MongoDB
        videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {
                "$set": {
                    "duration": duration_str,
                    "thumbnail_url": thumbnail_url,
                    "status": "done",
                }
            }
        )

    except Exception as e:
        print(f"[Celery] Error processing video {video_id}: {e}")
        videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"status": "error"}}
        )
        raise

    finally:
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
        if local_thumbnail_path and os.path.exists(local_thumbnail_path):
            os.remove(local_thumbnail_path)
