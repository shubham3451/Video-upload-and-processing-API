from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId
import os
from .db import videos_collection
from .celery_worker import process_video
from .gcs import upload_file_to_gcs
from .service import save_upload_file


app = FastAPI(title="Video Processing API")

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save video to a temp file locally before upload to GCS
    temp_dir = "/tmp/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    local_path = os.path.join(temp_dir, file.filename)


    video_gcs_path = f"videos/{file.filename}"
    try:
        # Step 1: Save to local temp path
        await save_upload_file(file, local_path)

        # Step 2: Upload to Google Cloud Storage
        try:
            gcs_url = upload_file_to_gcs(local_path, video_gcs_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GCS upload failed: {str(e)}")

        # Step 3: Insert into MongoDB
        video_doc = {
            "filename": file.filename,
            "upload_time": datetime.utcnow(),
            "status": "pending",
        }
        result = videos_collection.insert_one(video_doc)
        video_id = str(result.inserted_id)

        # Step 4: Trigger async Celery processing
        process_video.delay(video_id, video_gcs_path, file.filename)

        return {
            "id": video_id,
            "filename": video_doc["filename"],
            "upload_time": video_doc["upload_time"].isoformat(),
            "status": video_doc["status"],
        }

    finally:
        # Step 5: Clean up local temp file
        if os.path.exists(local_path):
            os.remove(local_path)
    

@app.get("/video-status/{id}")
def video_status(id: str):
    video = videos_collection.find_one({"_id": ObjectId(id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"status": video.get("status", "pending")}

@app.get("/video-metadata/{id}")
def video_metadata(id: str):
    video = videos_collection.find_one({"_id": ObjectId(id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    response = {
        "filename": video.get("filename"),
        "upload_time": video.get("upload_time").isoformat() if video.get("upload_time") else None,
        "status": video.get("status"),
        "duration": video.get("duration"),
        "thumbnail_url": video.get("thumbnail_url"),
    }
    return response
