from app.models.domain import ProductData, VideoScript
from app.config.settings import settings
from app.services.ai.huggingface_client import HuggingFaceClient
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.hf_client = None
        self.fallback_client = None
        
        # Initialize Hugging Face client (primary - free)
        self.hf_client = HuggingFaceClient(
            api_key=settings.HUGGINGFACE_API_KEY,
            model=settings.HUGGINGFACE_MODEL
        )
        
        # Initialize fallback client with simpler model
        self.fallback_client = HuggingFaceClient(
            api_key=settings.HUGGINGFACE_API_KEY,
            model="gpt2"  # Simpler, faster model as fallback
        )
        
        logger.info("ContentGenerator: Hugging Face Client initialized as primary AI service")
        logger.info("ContentGenerator: Fallback client initialized with gpt2 model")
    
    async def generate_video_script(self, product_data: ProductData) -> VideoScript:
        """Generate video script from product data"""
        logger.info("ContentGenerator: Generating video script from product data")
        
        # Log input product data
        logger.info(f"ContentGenerator: Input Product: {product_data.title}")
        logger.info(f"ContentGenerator: Product Price: {product_data.price}")
        logger.info(f"ContentGenerator: Product Description: {product_data.description[:100]}...")
        logger.info(f"ContentGenerator: Product Features: {len(product_data.features)} items")
        for i, feature in enumerate(product_data.features[:3], 1):
            logger.info(f"ContentGenerator: {i}. {feature}")
        
        # Create prompt for AI
        prompt = self._create_prompt(product_data)
        logger.info(f"ContentGenerator: Created prompt: {len(prompt)} characters")
        logger.info(f"ContentGenerator: Prompt preview: {prompt[:200]}...")
        
        # Try primary Hugging Face model
        if self.hf_client:
            try:
                logger.info("ContentGenerator: Attempting to generate content with primary Hugging Face model...")
                generated_content = await self.hf_client.generate_text(prompt, max_length=300)
                
                if generated_content:
                    logger.info("ContentGenerator: Successfully generated content with primary Hugging Face model")
                    logger.info(f"ContentGenerator: Raw AI Response: {generated_content}")
                    return self._parse_ai_response(generated_content, product_data)
                else:
                    logger.warning("ContentGenerator: Primary model failed - trying fallback model...")
            except Exception as e:
                logger.error(f"ContentGenerator: Primary Hugging Face model error: {str(e)}")
                logger.info("ContentGenerator: Trying fallback model...")
        
        # Try fallback model
        if self.fallback_client:
            try:
                logger.info("ContentGenerator: Attempting to generate content with fallback Hugging Face model (gpt2)...")
                # Use simpler prompt for gpt2
                simple_prompt = f"Product: {product_data.title}. Features: {', '.join(product_data.features[:2]) if product_data.features else 'High quality'}. Create a short ad:"
                generated_content = await self.fallback_client.generate_text(simple_prompt, max_length=150)
                
                if generated_content:
                    logger.info("ContentGenerator: Successfully generated content with fallback model")
                    logger.info(f"ContentGenerator: Raw AI Response: {generated_content}")
                    return self._parse_ai_response(generated_content, product_data)
                else:
                    logger.warning("ContentGenerator: Fallback model also failed - using template content...")
            except Exception as e:
                logger.error(f"ContentGenerator: Fallback Hugging Face model error: {str(e)}")
                logger.info("ContentGenerator: Using template content generation...")
        
        # Use template-based content generation
        logger.info("ContentGenerator: Using template-based content generation...")
        return self._create_template_script(product_data)
    
    def _create_prompt(self, product_data: ProductData) -> str:
        """Create a prompt for AI content generation"""
        prompt = f"""
            Create a compelling 30-second slideshow video advertisement script for this product:

            Product: {product_data.title}
            Description: {product_data.description}
            Price: {product_data.price if product_data.price else 'Not specified'}
            Features: {', '.join(product_data.features[:5]) if product_data.features else 'Not specified'}

            Requirements:
            - Create an engaging, punchy headline (max 8 words) that grabs attention
            - Write 4-5 compelling bullet points about the product benefits
            - Make it exciting and persuasive for social media
            - Keep it concise for a slideshow video with text overlays
            - Use action words and emotional triggers

            Format your response as:
            HEADLINE: [your punchy headline]
            BULLET POINTS (start bullet ponts with - or *): 
            - [benefit 1 - keep it short and impactful]
            - [benefit 2 - focus on value proposition]
            - [benefit 3 - create urgency or exclusivity]
            CALL TO ACTION: [strong call to action like "GET IT NOW!" or "SHOP TODAY!"]
            """
        return prompt.strip()
    
    def _parse_ai_response(self, response: str, product_data: ProductData) -> VideoScript:
        """Parse AI response into VideoScript"""
        try:
            logger.info(f"ContentGenerator: Parsing AI response: {len(response)} characters")
            logger.info(f"ContentGenerator: Full AI response: {response}")
            
            # Parse the response to extract headline and bullet points
            lines = response.strip().split('\n')
            headline = ""
            bullet_points = []
            call_to_action = "GET IT NOW!"  # Default CTA
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Extract headline (usually the first line or line with "HEADLINE:")
                if "HEADLINE:" in line.upper():
                    headline = line.split(":", 1)[1].strip()
                elif "TITLE:" in line.upper():
                    headline = line.split(":", 1)[1].strip()
                elif not headline and line and not line.startswith('•') and not line.startswith('-') and not line.startswith('CALL'):
                    # First non-bullet line is likely the headline
                    headline = line
                    
                # Extract bullet points
                elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    point = line.lstrip('•-* ').strip()
                    if point and len(point) > 5:
                        bullet_points.append(point)
                        logger.info(f"ContentGenerator: Found bullet point: {point}")
                        
                # Extract call to action
                elif "CALL TO ACTION:" in line.upper() or "CTA:" in line.upper():
                    call_to_action = line.split(":", 1)[1].strip()
                    logger.info(f"ContentGenerator: Found call to action: {call_to_action}")
                elif "GET IT NOW" in line.upper() or "SHOP" in line.upper() or "BUY" in line.upper():
                    call_to_action = line.strip()
                    logger.info(f"ContentGenerator: Found call to action: {call_to_action}")
            
            # Ensure we have a headline
            if not headline:
                headline = f"🚀 {product_data.title[:30].upper()} 🚀"
            
            # Ensure we have bullet points
            if not bullet_points:
                bullet_points = [
                    f"Premium {product_data.title.lower()}",
                    f"Only {product_data.price} - Limited Time!",
                    "Get it now before it's gone!"
                ]
            
            # Limit bullet points to 8
            bullet_points = bullet_points[:8]
            
            logger.info("ContentGenerator: Parsed AI response successfully:")
            logger.info(f"ContentGenerator: Headline: {headline}")
            logger.info(f"ContentGenerator: Bullet points: {len(bullet_points)} items")
            for i, point in enumerate(bullet_points, 1):
                logger.info(f"ContentGenerator: {i}. {point}")
            
            return VideoScript(
                headline=headline,
                bullet_points=bullet_points,
                call_to_action=call_to_action
            )
            
        except Exception as e:
            logger.error(f"ContentGenerator: Failed to parse AI response: {str(e)}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    def _create_template_script(self, product_data: ProductData) -> VideoScript:
        """Create template-based script when AI fails - more engaging than basic fallback"""
        logger.info("ContentGenerator: Creating template-based script")
        
        # Generate engaging headline
        headline = f"🚀 {product_data.title.upper()} - GAME CHANGER! 🚀"
        
        # Create bullet points from features
        bullet_points = []
        for i, feature in enumerate(product_data.features[:5]):
            # Clean up feature text
            clean_feature = feature.replace('**', '').replace('*', '').strip()
            if clean_feature:
                bullet_points.append(f"{clean_feature}")
        
        # Add price information if available
        if product_data.price:
            bullet_points.append(f"Only {product_data.price} - Limited Time!")
        
        # Ensure we have at least 3 bullet points
        while len(bullet_points) < 3:
            bullet_points.append("Premium quality you can trust")
        
        # Create call to action
        call_to_action = "GET IT NOW!"
        
        script = VideoScript(
            headline=headline,
            bullet_points=bullet_points,
            call_to_action=call_to_action
        )
        
        logger.info(f"ContentGenerator: Created template script: headline='{script.headline}', {len(script.bullet_points)} bullet points")
        return script
    
    def _create_fallback_script(self, product_data: ProductData) -> VideoScript:
        """Create a fallback script when AI generation fails"""
        logger.info("ContentGenerator: Creating fallback script...")
        
        # Create a simple but engaging script
        title = product_data.title or "Amazing Product"
        price = product_data.price or "Great Value"
        
        headline = f"🔥 {title[:25].upper()} - MUST HAVE! 🔥"
        
        bullet_points = [
            f"Premium {title.lower()} quality",
            f"Only {price} - Limited Time!",
            "Don't miss this amazing deal!"
        ]
        
        call_to_action = "GET IT NOW!"
        
        logger.info(f"ContentGenerator: Created fallback script: {headline}")
        return VideoScript(
            headline=headline,
            bullet_points=bullet_points,
            call_to_action=call_to_action
        ) 