from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Annotated
from datetime import datetime
from enum import Enum

# Status enum for validation
class VideoStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"


# Final metadata model
class VideoMetadata(BaseModel):
    filename: Annotated[str, Field(min_length=1, max_length=255)]
    upload_time: Annotated[datetime, Field(description="UTC time of upload")]
    status: Annotated[VideoStatus, Field(description="Processing status")]
    duration: Optional[Annotated[str, Field(pattern=r"^\d{2}:\d{2}:\d{2}$",description="Duration in HH:MM:SS format"
    )]] = None
    thumbnail_url: Optional[Annotated[HttpUrl, Field(description="Public URL of thumbnail")]] = None
