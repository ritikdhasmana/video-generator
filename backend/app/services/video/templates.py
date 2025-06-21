"""
Video Templates System
Provides different visual styles and templates for video generation
"""

from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class TextStyle:
    """Text styling configuration"""
    font_size: int
    color: Tuple[int, int, int]  # RGB
    outline_color: Tuple[int, int, int]  # RGB
    background_color: Tuple[int, int, int, int]  # RGBA
    font_family: str
    font_weight: str = "normal"
    shadow: bool = True
    gradient: bool = False
    animation: str = "fade"  # fade, slide, bounce, typewriter

@dataclass
class VideoTemplate:
    """Video template configuration"""
    name: str
    description: str
    background_style: str  # solid, gradient, pattern
    background_colors: List[Tuple[int, int, int]]
    text_styles: Dict[str, TextStyle]  # headline, bullet, cta
    animation_speed: float
    transition_style: str  # crossfade, slide, zoom
    overall_theme: str  # modern, classic, bold, elegant

class VideoTemplateManager:
    """Manages video templates and styling"""
    
    def __init__(self):
        self.templates = self._create_default_templates()
    
    def _create_default_templates(self) -> Dict[str, VideoTemplate]:
        """Create default video templates"""
        templates = {}
        
        # Modern Bold Template - Bright yellow text on dark backgrounds
        templates["modern_bold"] = VideoTemplate(
            name="Modern Bold",
            description="Bold, vibrant colors with modern typography",
            background_style="gradient",
            background_colors=[(255, 87, 51), (255, 45, 85)],  # Orange to Pink gradient
            text_styles={
                "headline": TextStyle(
                    font_size=80,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 200),  # Very dark background
                    font_family="Arial-Bold",
                    shadow=True,
                    gradient=True,
                    animation="slide"
                ),
                "bullet": TextStyle(
                    font_size=55,
                    color=(255, 255, 255),  # White text
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 180),  # Dark background
                    font_family="Arial",
                    shadow=True,
                    animation="fade"
                ),
                "cta": TextStyle(
                    font_size=50,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(255, 0, 0, 220),  # Bright red background
                    font_family="Arial-Bold",
                    shadow=True,
                    gradient=True,
                    animation="bounce"
                )
            },
            animation_speed=1.2,
            transition_style="crossfade",
            overall_theme="modern"
        )
        
        # Elegant Professional Template - White text on dark blue backgrounds
        templates["elegant_pro"] = VideoTemplate(
            name="Elegant Professional",
            description="Clean, professional look with subtle animations",
            background_style="gradient",
            background_colors=[(41, 128, 185), (52, 152, 219)],  # Blue gradient
            text_styles={
                "headline": TextStyle(
                    font_size=75,
                    color=(255, 255, 255),  # White text
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 200),  # Very dark background
                    font_family="Helvetica",
                    shadow=True,
                    animation="fade"
                ),
                "bullet": TextStyle(
                    font_size=50,
                    color=(255, 255, 255),  # White text
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 180),  # Dark background
                    font_family="Helvetica",
                    shadow=True,
                    animation="fade"
                ),
                "cta": TextStyle(
                    font_size=65,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 128, 0, 220),  # Bright green background
                    font_family="Helvetica-Bold",
                    shadow=True,
                    animation="slide"
                )
            },
            animation_speed=1.0,
            transition_style="crossfade",
            overall_theme="elegant"
        )
        
        # Vibrant Social Template - Bright colors for maximum visibility
        templates["vibrant_social"] = VideoTemplate(
            name="Vibrant Social",
            description="Eye-catching colors perfect for social media",
            background_style="gradient",
            background_colors=[(155, 89, 182), (142, 68, 173)],  # Purple gradient
            text_styles={
                "headline": TextStyle(
                    font_size=75,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 220),  # Very dark background
                    font_family="Arial-Bold",
                    shadow=True,
                    gradient=True,
                    animation="bounce"
                ),
                "bullet": TextStyle(
                    font_size=60,
                    color=(255, 255, 255),  # White text
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 200),  # Dark background
                    font_family="Arial",
                    shadow=True,
                    animation="slide"
                ),
                "cta": TextStyle(
                    font_size=55,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(255, 0, 0, 240),  # Bright red background
                    font_family="Arial-Bold",
                    shadow=True,
                    gradient=True,
                    animation="bounce"
                )
            },
            animation_speed=1.5,
            transition_style="slide",
            overall_theme="vibrant"
        )
        
     
        #  High Visibility Template - Maximum contrast for any background
        templates["high_visibility"] = VideoTemplate(
            name="High Visibility",
            description="Maximum contrast colors for visibility on any background",
            background_style="gradient",
            background_colors=[(255, 0, 0), (255, 165, 0)],  # Red to Orange gradient
            text_styles={
                "headline": TextStyle(
                    font_size=75,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 250),  # Almost solid black background
                    font_family="Arial-Bold",
                    shadow=True,
                    gradient=True,
                    animation="slide"
                ),
                "bullet": TextStyle(
                    font_size=60,
                    color=(255, 255, 255),  # Pure white text
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(0, 0, 0, 240),  # Very dark background
                    font_family="Arial-Bold",
                    shadow=True,
                    animation="slide"
                ),
                "cta": TextStyle(
                    font_size=65,
                    color=(255, 255, 0),  # Bright yellow
                    outline_color=(0, 0, 0),  # Black outline
                    background_color=(255, 0, 0, 250),  # Solid red background
                    font_family="Arial-Bold",
                    shadow=True,
                    gradient=True,
                    animation="bounce"
                )
            },
            animation_speed=1.5,
            transition_style="crossfade",
            overall_theme="high_visibility"
        )
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[VideoTemplate]:
        """Get a specific template by name"""
        return self.templates.get(template_name, self.templates["high_visibility"])
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                "name": template.name,
                "description": template.description,
                "theme": template.overall_theme
            }
            for template in self.templates.values()
        ]
    
    def get_font_path(self, font_family: str) -> str:
        """Get the path to a font file"""
        # Common font paths for different systems
        font_paths = {
            "Arial": "/System/Library/Fonts/Arial.ttf",
            "Arial-Bold": "/System/Library/Fonts/Arial Bold.ttf",
            "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
            "Helvetica-Bold": "/System/Library/Fonts/Helvetica Bold.ttf",
            "Times": "/System/Library/Fonts/Times.ttc",
            "Times-Bold": "/System/Library/Fonts/Times Bold.ttf"
        }
        
        # Try to find the font
        font_path = font_paths.get(font_family, font_paths["Arial"])
        
        if os.path.exists(font_path):
            return font_path
        
        # Fallback to system default
        logger.warning(f"Font {font_family} not found, using default")
        return "/System/Library/Fonts/Arial.ttf"
    
    def create_gradient_background(self, colors: List[Tuple[int, int, int]], size: Tuple[int, int]) -> str:
        """Create a gradient background image"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', size)
            draw = ImageDraw.Draw(img)
            
            if len(colors) == 1:
                # Solid color
                draw.rectangle([0, 0, size[0], size[1]], fill=colors[0])
            else:
                # Gradient (simple linear gradient)
                for y in range(size[1]):
                    ratio = y / size[1]
                    r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                    g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                    b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                    draw.line([(0, y), (size[0], y)], fill=(r, g, b))
            
            # Save temporary file
            temp_path = f"./storage/images/gradient_bg_{hash(str(colors))}.png"
            os.makedirs("./storage/images", exist_ok=True)
            img.save(temp_path, 'PNG')
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create gradient background: {e}")
            return None 