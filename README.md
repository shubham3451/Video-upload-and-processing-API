
#  Video Upload & Processing API

A FastAPI-based backend to upload videos, extract metadata, and generate thumbnails asynchronously using **Celery + Redis**. Media is stored in **Google Cloud Storage**, and video processing is done using **FFmpeg**.

---

## 🚀 Features

- ✅ Upload video files via API
- ✅ Store videos in Google Cloud Storage
- ✅ Extract video duration
- ✅ Generate a thumbnail at 10% of video duration
- ✅ Store metadata in MongoDB
- ✅ Async processing with Celery + Redis
- ✅ Containerized with Docker

---

## 🧰 Tech Stack

- **FastAPI** (async API)
- **MongoDB** with PyMongo (sync)
- **Celery + Redis** for background processing
- **FFmpeg** for video processing
- **Google Cloud Storage** (GCS) for file uploads
- **Docker & Docker Compose**

---

## ⚙️ Setup & Run Instructions

### 1. 🔧 Prerequisites

- Docker + Docker Compose installed
- A GCS bucket with credentials
- FFmpeg (installed inside Docker automatically)

---

### 2. 🧪 Clone the repository

```bash
git clone https://github.com/your-username/clipo.git
cd clipo
````

---

### 3. 🔐 Add your environment variables to `.env`

```env
MONGO_URI=mongodb://mongo:27017
REDIS_BROKER_URL=redis://redis:6379/0
GCS_BUCKET_NAME=your-gcs-bucket-name
THUMBNAILS_DIR=/tmp/thumbnails
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
```

> Place your `credentials.json` (GCP service account) inside the project directory.

---

### 4. 🐳 Start the application using Docker Compose

```bash
docker-compose up --build
```

* API available at: [http://localhost:8000](http://localhost:8000)
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔁 Sample API Requests

### 🔼 Upload Video

```bash
curl -X POST http://localhost:8000/upload-video/ \
  -F "file=@/path/to/video.mp4"
```

Response:

```json
{
  "video_id": "665b9e2d45ab4a83968f234c",
  "message": "Upload successful and processing started."
}
```

---

### 📊 Get Video Status

```bash
curl http://localhost:8000/video-status/665b9e2d45ab4a83968f234c
```

Response:

```json
{
  "status": "processing"
}
```

---

### 📄 Get Full Metadata

```bash
curl http://localhost:8000/video-metadata/665b9e2d45ab4a83968f234c
```

Response:

```json
{
  "filename": "example.mp4",
  "upload_time": "2025-06-14T10:00:00",
  "status": "done",
  "duration": "00:02:45",
  "thumbnail_url": "https://storage.googleapis.com/your-bucket/thumbnails/665b9e2d45ab4a83968f234c.jpg"
}
```

---

## 🛠 FFmpeg Commands Used

1. **Extract Duration (used internally via ffmpeg-python)**

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
```

2. **Generate Thumbnail**

```bash
ffmpeg -ss <timestamp> -i input.mp4 -frames:v 1 -q:v 2 output.jpg
```

* `<timestamp>` = 10% of duration (e.g., `00:00:12`)
* `-frames:v 1` = extract only 1 frame
* `-q:v 2` = high-quality image

---

## 🧹 Cleanup

To stop containers:

```bash
docker-compose down
```

To remove all volumes & networks:

```bash
docker-compose down -v --remove-orphans
```


## 📄 License

MIT License. Free to use and modify.

---

