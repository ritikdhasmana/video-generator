from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductData(BaseModel):
    title: str
    price: str
    description: str
    features: List[str]
    images: List[str]
    rating: Optional[str] = None
    availability: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None

class VideoScript(BaseModel):
    headline: str
    bullet_points: List[str]
    call_to_action: str

class VideoGenerationRequest(BaseModel):
    url: str
    aspect_ratio: str = "16:9"
    duration: int = 30
    template: str = "high_visibility"  # Default template for maximum visibility

class VideoGenerationResponse(BaseModel):
    video_id: str
    status: str
    download_url: Optional[str] = None
    estimated_duration: int = 30 # Or whatever is appropriate
    created_at:datetime=datetime.now()

class VideoStatusResponse(BaseModel):
    video_id: str
    status: str
    progress: float = 0.0
    message: str = ""
    video_path: str = ""
