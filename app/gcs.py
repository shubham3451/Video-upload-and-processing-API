from google.cloud import storage
from .config import GCS_BUCKET_NAME

def upload_file_to_gcs(local_path: str, destination_blob_name: str, timeout: float = 300) -> str:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_path, timeout=timeout)
    return f"https://storage.googleapis.com/{bucket.name}/{blob.name}"

def upload_bytes_to_gcs(data: bytes, destination_blob_name: str, content_type="application/octet-stream", timeout: float = 300) -> str:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data, content_type=content_type, timeout=timeout)
    blob.make_public()
    return blob.public_url

