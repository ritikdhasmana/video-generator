from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
from moviepy.video.fx.all import resize, crop
from app.models.domain import VideoScript, ProductData
import os
import uuid
from typing import List
import httpx
from PIL import Image, ImageDraw, ImageFont
import io
import logging
import json
import asyncio
import subprocess
import tempfile
import numpy as np
from app.services.video.templates import VideoTemplateManager

# Set up logging
logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.video_size = (1920, 1080)  # Default 16:9
        self.template_manager = VideoTemplateManager()
        logger.info("VideoGenerator: Initialized")
    
    async def generate_video(self, script: VideoScript, product_data: ProductData, 
                           aspect_ratio: str = "16:9", duration: int = 30, 
                           template_name: str = "modern_bold") -> str:
        """Generate social media style video with dynamic image slideshow and sequential text"""
        
        logger.info(f"generate_video: Starting with template: {template_name}")
        
        try:
            # Get template
            template = self.template_manager.get_template(template_name)
            logger.info(f"generate_video: Using template: {template.name}")
            
            # Create video ID
            video_id = str(uuid.uuid4())
            logger.info(f"generate_video: Video ID: {video_id}")
            
            # Set video size based on aspect ratio
            if aspect_ratio == "9:16":
                self.video_size = (1080, 1920)
                logger.info("generate_video: Using vertical format (9:16)")
            else:
                self.video_size = (1920, 1080)
                logger.info("generate_video: Using horizontal format (16:9)")
            
            # Create dynamic image slideshow background
            logger.info("generate_video: Creating dynamic image slideshow")
            background_clip = await self._create_dynamic_image_slideshow(product_data, duration, video_id, template)
            
            # Create sequential text overlays
            logger.info("generate_video: Creating sequential text overlays")
            text_clips = self._create_sequential_text_overlays(script, duration, template)
            
            # Calculate actual video duration based on content
            actual_duration = self._calculate_actual_duration(text_clips, duration)
            logger.info(f"generate_video: Actual video duration: {actual_duration} seconds")
            
            # Trim background to actual duration
            background_clip = background_clip.subclip(0, actual_duration)
            
            # Combine background and text
            clips = [background_clip]
            clips.extend(text_clips)
            
            final_video = CompositeVideoClip(clips, size=self.video_size)
            
            # Ensure storage directory exists
            os.makedirs("./storage/videos", exist_ok=True)
            
            # Export video
            output_path = f"./storage/videos/{video_id}.mp4"
            logger.info(f"generate_video: Exporting video to: {output_path}")
            
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            logger.info(f"generate_video: Video generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"generate_video: Failed to generate video: {str(e)}")
            raise
    
    async def _create_dynamic_image_slideshow(self, product_data: ProductData, duration: int, 
                                            video_id: str, template) -> VideoFileClip:
        """Create dynamic image slideshow with template-based styling"""
        try:
            image_clips = []
            images = product_data.images[:8]  # Limit to 8 images for better performance
            
            if not images:
                logger.warning("_create_dynamic_image_slideshow: No images available, using gradient background")
                return self._create_gradient_background_clip(template, duration)
            
            logger.info(f"_create_dynamic_image_slideshow: Processing {len(images)} images")
            
            for i, image_url in enumerate(images):
                try:
                    logger.info(f"_create_dynamic_image_slideshow: Downloading image {i+1}/{len(images)}")
                    
                    # Download and process image
                    logger.info(image_url)
                    image = await self._download_and_process_image(image_url, video_id, i)
                    if not image:
                        continue
                    
                    # Resize image to fit video dimensions
                    resized_image = self._resize_image_to_fit(image, self.video_size)
                    
                    # Save processed image
                    image_filename = f"product_{video_id}_{i}.jpg"
                    image_path = f"./storage/images/{image_filename}"
                    resized_image.save(image_path, 'JPEG', quality=85)
                    
                    # Create video clip with animation
                    clip_duration = duration / len(images)
                    clip = ImageClip(image_path, duration=clip_duration)
                    
                    # Apply template-based animation
                    animation_type = i % 4  # Cycle through 4 animation types
                    animated_clip = self._apply_template_animation(clip, animation_type, clip_duration, template)
                    
                    image_clips.append(animated_clip)
                    logger.info(f"_create_dynamic_image_slideshow: Image {i+1} processed")
                    
                except Exception as e:
                    logger.error(f"_create_dynamic_image_slideshow: Failed to process image {i+1}: {str(e)}")
                    continue
            
            if not image_clips:
                logger.warning("_create_dynamic_image_slideshow: No images processed successfully, using gradient background")
                return self._create_gradient_background_clip(template, duration)
            
            # Concatenate image clips with template-based transitions
            if len(image_clips) == 1:
                return image_clips[0]
            
            # Add template-based transitions
            transition_duration = 0.4 * template.animation_speed
            final_clips = []
            
            for i, clip in enumerate(image_clips):
                if i > 0:
                    # Add template-based transition
                    if template.transition_style == "crossfade":
                        clip = clip.crossfadein(transition_duration)
                    elif template.transition_style == "slide":
                        clip = clip.set_position(('right', 0)).crossfadein(transition_duration)
                    elif template.transition_style == "zoom":
                        clip = clip.resize(lambda t: 1 + 0.1 * t).crossfadein(transition_duration)
                final_clips.append(clip)
            
            # Concatenate all clips
            slideshow = concatenate_videoclips(final_clips, method="compose")
            logger.info(f"_create_dynamic_image_slideshow: Slideshow created with {len(image_clips)} images")
            return slideshow
                
        except Exception as e:
            logger.error(f"_create_dynamic_image_slideshow: Failed to create slideshow: {str(e)}")
            return self._create_gradient_background_clip(template, duration)
    
    def _create_gradient_background_clip(self, template, duration: int) -> ColorClip:
        """Create gradient background clip based on template"""
        try:
            if template.background_style == "gradient" and len(template.background_colors) > 1:
                # Create gradient background
                gradient_path = self.template_manager.create_gradient_background(
                    template.background_colors, self.video_size
                )
                if gradient_path and os.path.exists(gradient_path):
                    return ImageClip(gradient_path, duration=duration)
            
            # Fallback to solid color
            color = template.background_colors[0]
            return ColorClip(size=self.video_size, color=color, duration=duration)
            
        except Exception as e:
            logger.error(f"_create_gradient_background_clip: Failed to create gradient background: {e}")
            return ColorClip(size=self.video_size, color=(25, 25, 112), duration=duration)
    
    def _apply_template_animation(self, clip, animation_type: int, clip_duration: float, template):
        """Apply template-based animation to clip"""
        try:
            if animation_type == 0:
                # Zoom in effect
                def zoom_in_effect(get_frame, t):
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    zoom_factor = 1 + 0.1 * (t / clip_duration)
                    new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
                    start_h, start_w = (h - new_h) // 2, (w - new_w) // 2
                    cropped = frame[start_h:start_h + new_h, start_w:start_w + new_w]
                    return cropped.astype('uint8')
                return clip.fl(zoom_in_effect)
                
            elif animation_type == 1:
                # Pan effect
                def pan_effect(get_frame, t):
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    pan_amount = int(0.1 * w * t / clip_duration)
                    return frame[:, pan_amount:pan_amount + w]
                return clip.fl(pan_effect)
                
            elif animation_type == 2:
                # Fade effect with template colors
                def fade_effect(get_frame, t):
                    frame = get_frame(t)
                    if t < clip_duration * 0.1:
                        opacity = t / (clip_duration * 0.1)
                    elif t > clip_duration * 0.9:
                        opacity = (clip_duration - t) / (clip_duration * 0.1)
                    else:
                        opacity = 1.0
                    return (frame * opacity).astype('uint8')
                return clip.fl(fade_effect)
                
            else:
                # Rotate zoom effect
                def rotate_zoom_effect(get_frame, t):
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    zoom_factor = 1 + 0.05 * (t / clip_duration)
                    new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
                    start_h, start_w = (h - new_h) // 2, (w - new_w) // 2
                    cropped = frame[start_h:start_h + new_h, start_w:start_w + new_w]
                    if t > clip_duration / 2:
                        cropped = cropped * 1.05  # Brighten slightly
                    return cropped.astype('uint8')
                return clip.fl(rotate_zoom_effect)
                
        except Exception as e:
            logger.error(f"_apply_template_animation: Failed to apply animation: {e}")
            return clip
    
    async def _download_and_process_image(self, image_url: str, video_id: str, index: int) -> Image.Image:
        """Download and process image"""
        try:
            logger.info(f"_download_and_process_image: Fetching image {index+1} from URL: {image_url}")

            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(image_url, timeout=10)
                response.raise_for_status()
                
                image = Image.open(io.BytesIO(response.content))
                logger.info(f"_download_and_process_image: Image {index+1} downloaded successfully")
                
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                return image
                
        except Exception as e:
            logger.error(f"_download_and_process_image: Failed to download image {index+1} from {image_url}: {str(e)}")
            return None

    # async def _download_and_process_image(self, image_url: str, video_id: str, index: int) -> Image.Image:
    #     """Download and process image"""
    #     try:
    #         async with httpx.AsyncClient(verify=False) as client:
    #             response = await client.get(image_url, timeout=10)
    #             response.raise_for_status()
                
    #             # Load image
    #             image = Image.open(io.BytesIO(response.content))
    #             logger.info(f"_download_and_process_image: Image {index+1} downloaded successfully")
                
    #             # Convert to RGB if necessary
    #             if image.mode != 'RGB':
    #                 image = image.convert('RGB')
                
    #             return image
                
    #     except Exception as e:
    #         logger.error(f"_download_and_process_image: Failed to download image {index+1}: {str(e)}")
    #         return None
    
    def _resize_image_to_fit(self, image: Image.Image, target_size: tuple) -> Image.Image:
        """Resize image to fit target size while maintaining aspect ratio"""
        try:
            target_width, target_height = target_size
            
            # Get image dimensions
            img_width, img_height = image.size
            
            # Calculate aspect ratios
            target_ratio = target_width / target_height
            img_ratio = img_width / img_height
            
            if img_ratio > target_ratio:
                # Image is wider, fit to width
                new_width = target_width
                new_height = int(target_width / img_ratio)
            else:
                # Image is taller, fit to height
                new_height = target_height
                new_width = int(target_height * img_ratio)
            
            # Resize image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create new image with target size and black background
            final_image = Image.new('RGB', target_size, (0, 0, 0))
            
            # Paste resized image in center
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            final_image.paste(resized_image, (paste_x, paste_y))
            
            return final_image
            
        except Exception as e:
            logger.error(f"_resize_image_to_fit: Failed to resize image: {str(e)}")
            return Image.new('RGB', target_size, (25, 25, 112))
    
    def _create_sequential_text_overlays(self, script: VideoScript, duration: int, template) -> List:
        """Create sequential text overlays with template-based styling"""
        text_clips = []
        
        # Prepare text lines
        text_lines = []
        
        # Add headline
        if script.headline:
            text_lines.append(("headline", script.headline))
        
        # Add bullet points
        if script.bullet_points:
            for point in script.bullet_points[:5]:
                clean_point = point.replace('**', '').replace('*', '')
                if ':' in clean_point:
                    clean_point = clean_point.split(':', 1)[1].strip()
                text_lines.append(("bullet", f"{clean_point}"))
        
        # Add call to action
        text_lines.append(("cta", script.call_to_action))
        
        # Calculate timing - better distribution
        total_lines = len(text_lines)
        if total_lines == 0:
            return text_clips
        
        # Each line gets 3-4 seconds, with proper spacing
        line_duration = min(4.0, duration / total_lines)
        fade_duration = 0.8 * template.animation_speed
        
        for i, (text_type, text) in enumerate(text_lines):
            # Calculate start time (better spacing)
            start_time = i * (line_duration * 0.8)  # 20% overlap for better flow
            
            # Get text style from template
            text_style = template.text_styles.get(text_type, template.text_styles["headline"])
            
            # Create text clip with template styling
            text_clip = self._create_styled_text_clip(
                text, text_style, template, line_duration, start_time, fade_duration, i, total_lines
            )
            
            if text_clip:
                text_clips.append(text_clip)
                logger.info(f"_create_sequential_text_overlays: Text line {i+1} added")
        
        return text_clips
    
    def _create_styled_text_clip(self, text: str, text_style, template, duration: float, 
                               start_time: float, fade_duration: float, index: int, total_lines: int):
        """Create text clip with template-based styling"""
        try:
            # Create a PIL image with text and background
            img = Image.new('RGBA', self.video_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Get font
            font_path = self.template_manager.get_font_path(text_style.font_family)
            try:
                font = ImageFont.truetype(font_path, text_style.font_size)
            except:
                font = ImageFont.load_default()
            
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position (center horizontally, different vertical positions)
            x = (self.video_size[0] - text_width) // 2
            
            # Different vertical positions for each text element
            if index == 0:  # Headline
                y = int(self.video_size[1] * 0.15)  # Top area
            elif index == total_lines - 1:  # CTA
                y = int(self.video_size[1] * 0.75)  # Bottom area
            else:  # Bullet points
                y = int(self.video_size[1] * 0.35) + (index * 80)  # Middle area with spacing
            
            # Create background rectangle with template styling
            padding = 30  # Increased padding for better visibility
            bg_x1 = x - padding
            bg_y1 = y - padding
            bg_x2 = x + text_width + padding
            bg_y2 = y + text_height + padding
            
            # Draw background rectangle with higher opacity
            background_color = list(text_style.background_color)
            background_color[3] = min(255, background_color[3] + 20)  # Increase opacity
            draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], 
                         fill=tuple(background_color))
            
            # Draw text with outline for better visibility
            outline_color = text_style.outline_color
            # Draw thicker outline for better visibility
            for dx in [-3, -2, -1, 0, 1, 2, 3]:
                for dy in [-3, -2, -1, 0, 1, 2, 3]:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=text_style.color)
            
            # Save temporary image
            temp_path = f"./storage/images/text_{uuid.uuid4()}.png"
            os.makedirs("./storage/images", exist_ok=True)
            img.save(temp_path, 'PNG')
            
            # Create video clip
            text_clip = ImageClip(temp_path, duration=duration)
            
            # Apply template-based animation
            animated_clip = self._apply_text_animation(
                text_clip, text_style.animation, duration, fade_duration, start_time
            )
            
            # Clean up
            os.remove(temp_path)
            
            return animated_clip
            
        except Exception as e:
            logger.error(f"_create_styled_text_clip: Failed to create styled text clip: {str(e)}")
            return None
    
    def _apply_text_animation(self, text_clip, animation_type: str, duration: float, 
                            fade_duration: float, start_time: float):
        """Apply template-based text animation"""
        try:
            if animation_type == "fade":
                # Simple fade in/out
                def fade_animation(get_frame, t):
                    frame = get_frame(t)
                    if t < fade_duration:
                        opacity = t / fade_duration
                    elif t > duration - fade_duration:
                        opacity = (duration - t) / fade_duration
                    else:
                        opacity = 1.0
                    if frame.shape[2] == 4:
                        frame = frame.copy()
                        frame[..., 3] = (frame[..., 3].astype(float) * opacity).astype('uint8')
                    return frame
                return text_clip.fl(fade_animation).set_start(start_time)
                
            elif animation_type == "slide":
                # Slide in from left
                def slide_animation(get_frame, t):
                    frame = get_frame(t)
                    if t < fade_duration:
                        progress = t / fade_duration
                        offset = int((1 - progress) * 100)
                        return frame[:, offset:offset + frame.shape[1]]
                    return frame
                return text_clip.fl(slide_animation).set_start(start_time)
                
            elif animation_type == "bounce":
                # Bounce effect
                def bounce_animation(get_frame, t):
                    frame = get_frame(t)
                    if t < fade_duration:
                        progress = t / fade_duration
                        scale = 0.5 + 0.5 * progress
                        # Simple scale effect
                        h, w = frame.shape[:2]
                        new_h, new_w = int(h * scale), int(w * scale)
                        if new_h > 0 and new_w > 0:
                            from PIL import Image
                            pil_img = Image.fromarray(frame)
                            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            frame = np.array(pil_img)
                    return frame
                return text_clip.fl(bounce_animation).set_start(start_time)
                
            else:
                # Default fade animation
                return text_clip.set_start(start_time)
                
        except Exception as e:
            logger.error(f"_apply_text_animation: Failed to apply text animation: {e}")
            return text_clip.set_start(start_time)
    
    def _calculate_actual_duration(self, text_clips: List, max_duration: int) -> float:
        """Calculate actual video duration based on content"""
        if not text_clips:
            return min(15.0, max_duration)
        
        # Find the latest end time of any text clip
        latest_end = 0
        for clip in text_clips:
            end_time = clip.start + clip.duration
            latest_end = max(latest_end, end_time)
        
        # Add some buffer time after last text
        actual_duration = latest_end + 3.0  # 3 seconds buffer
        
        # Cap at max duration
        actual_duration = min(actual_duration, max_duration)
        
        # Minimum 15 seconds
        actual_duration = max(actual_duration, 15.0)
        
        return actual_duration 