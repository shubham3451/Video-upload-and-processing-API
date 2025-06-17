import ffmpeg
from fastapi import UploadFile
import aiofiles

def get_video_duration(path: str) -> float:
    """Returns duration in seconds"""
    try:
        probe = ffmpeg.probe(path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        raise RuntimeError(f"Could not get video duration: {e}")

def generate_thumbnail(input_path: str, output_path: str, time_position: float):
    """
    Generate thumbnail at given time_position (in seconds)
    and save to output_path
    """
    try:
        (
            ffmpeg
            .input(input_path, ss=time_position)
            .filter('scale', 320, -1)
            .output(output_path, vframes=1)
            .overwrite_output()
            .run(quiet=True)
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate thumbnail: {e}")


async def save_upload_file(upload_file: UploadFile, destination_path: str):
    async with aiofiles.open(destination_path, 'wb') as out_file:
        while chunk := await upload_file.read(1024 * 1024):
            await out_file.write(chunk)