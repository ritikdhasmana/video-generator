from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.models.domain import VideoGenerationRequest, VideoGenerationResponse, VideoStatusResponse
from app.services.scraping.scraper import WebScraper
from app.services.ai.content_gen import ContentGenerator
from app.services.video.generator import VideoGenerator
from app.services.video.templates import VideoTemplateManager
import logging
import json
import os
import uuid
from typing import Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

# In-memory storage for video status (in production, use Redis or database)
video_status: Dict[str, Dict[str, Any]] = {}

router = APIRouter()

def load_video_status():
    """Load video status from JSON file"""
    try:
        if os.path.exists("./storage/video_status/status.json"):
            with open("./storage/video_status/status.json", "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load video status: {e}")
    return {}

def save_video_status():
    """Save video status to JSON file"""
    try:
        os.makedirs("./storage/video_status", exist_ok=True)
        with open("./storage/video_status/status.json", "w") as f:
            json.dump(video_status, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save video status: {e}")

# Load existing status on startup
video_status.update(load_video_status())

# Recover completed videos
for video_id, status_data in video_status.items():
    if status_data.get("status") == "completed" and status_data.get("video_path"):
        video_path = status_data["video_path"]
        if os.path.exists(video_path):
            logger.info(f"Recovered completed video: {video_id}")

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate video from product URL"""
    logger.info("Starting video generation request...")
    logger.info(f"Request details: URL={request.url}, Duration={request.duration}s, Aspect={request.aspect_ratio}")
    
    try:
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        logger.info(f"Generated video ID: {video_id}")
        
        # Initialize services
        logger.info("Initializing services...")
        scraper = WebScraper()
        content_generator = ContentGenerator()
        video_generator = VideoGenerator()
        template_manager = VideoTemplateManager()
        logger.info("Services initialized")
        
        # Validate template
        if not template_manager.get_template(request.template):
            raise HTTPException(status_code=400, detail=f"Invalid template: {request.template}")
        
        # Initialize video status
        video_status[video_id] = {
            "status": "generating",
            "progress": 0,
            "url": request.url,
            "template": request.template,
            "aspect_ratio": request.aspect_ratio,
            "duration": request.duration
        }
        logger.info(f"Status updated: {video_id} -> generating")
        
        # Start background task
        logger.info("Starting background task...")
        background_tasks.add_task(
            generate_video_background,
            video_id,
            request.url,
            request.template,
            request.aspect_ratio,
            request.duration
        )
        logger.info("Background task started")
        
        # Save status
        save_video_status()
        
        return VideoGenerationResponse(
            video_id=video_id,
            status="generating",
            message="Video generation started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start video generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}", response_model=VideoStatusResponse)
async def get_video_status(video_id: str):
    """Get video generation status"""
    logger.info(f"Checking status for video ID: {video_id}")
    
    if video_id not in video_status:
        logger.warning(f"Video ID not found: {video_id}")
        raise HTTPException(status_code=404, detail="Video not found")
    
    status_data = video_status[video_id]
    logger.info(f"Status for {video_id}: {status_data['status']}, Progress: {status_data.get('progress', 0)}%")
    
    return VideoStatusResponse(
        video_id=video_id,
        status=status_data["status"],
        progress=status_data.get("progress", 0),
        message=status_data.get("message", ""),
        video_path=status_data.get("video_path", "")
    )

@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """Download generated video"""
    logger.info(f"Download request for video ID: {video_id}")
    
    if video_id not in video_status:
        logger.warning(f"Video ID not found for download: {video_id}")
        raise HTTPException(status_code=404, detail="Video not found")
    
    status_data = video_status[video_id]
    if status_data["status"] != "completed":
        logger.warning(f"Video not ready for download: {video_id} - Status: {status_data['status']}")
        raise HTTPException(status_code=400, detail="Video not ready for download")
    
    file_path = status_data.get("video_path", "")
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Video file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Video file not found")
    
    logger.info(f"Serving video file: {file_path}")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=f"video_{video_id}.mp4"
    )

@router.get("/templates")
async def get_templates():
    """Get available video templates"""
    template_manager = VideoTemplateManager()
    templates = template_manager.get_all_templates()
    return {"templates": templates}

async def generate_video_background(
    video_id: str,
    url: str,
    template_name: str,
    aspect_ratio: str,
    duration: int
):
    """Background task for video generation"""
    logger.info(f"Background task started for video ID: {video_id}")
    logger.info(f"Using template: {template_name}")
    
    try:
        # Initialize services
        scraper = WebScraper()
        content_generator = ContentGenerator()
        video_generator = VideoGenerator()
        
        # Update progress
        video_status[video_id]["progress"] = 10
        logger.info(f"Progress updated: {video_id} -> 10%")
        
        # Step 1: Scrape product data
        logger.info(f"Step 1: Scraping product data from {url}")
        product_data = await scraper.scrape_product_data(url)
        video_status[video_id]["progress"] = 30
        logger.info(f"Progress updated: {video_id} -> 30%")
        logger.info(f"Product data extracted: {product_data.title}")
        
        # Step 2: Generate AI content
        logger.info("Step 2: Starting AI content generation...")
        script = await content_generator.generate_video_script(product_data)
        video_status[video_id]["progress"] = 60
        logger.info("AI content generation completed")
        logger.info(f"Content generated: {script.headline}")
        
        # Step 3: Generate video
        logger.info(f"Step 3: Generating video with template '{template_name}'")
        video_path = await video_generator.generate_video(
            script=script,
            product_data=product_data,
            aspect_ratio=aspect_ratio,
            duration=duration,
            template_name=template_name
        )
        video_status[video_id]["progress"] = 90
        logger.info(f"Progress updated: {video_id} -> 90%")
        logger.info(f"Video generated: {video_path}")
        
        # Update final status
        video_status[video_id].update({
            "status": "completed",
            "progress": 100,
            "video_path": video_path,
            "message": "Video generated successfully"
        })
        logger.info(f"Progress updated: {video_id} -> 100%")
        logger.info(f"Video generation completed successfully: {video_id}")
        
        # Save status
        save_video_status()
        
    except Exception as e:
        logger.error(f"Video generation failed for {video_id}: {str(e)}")
        video_status[video_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Video generation failed: {str(e)}"
        })
        logger.info(f"Status updated: {video_id} -> failed")
        save_video_status() 