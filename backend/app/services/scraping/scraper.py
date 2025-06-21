import httpx
import logging
from bs4 import BeautifulSoup
from app.models.domain import ProductData
from typing import List, Optional
import re
from urllib.parse import urljoin, urlparse

# Set up logging
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = None
    
    async def scrape_product_data(self, url: str) -> ProductData:
        """Scrape product data from a given URL"""
        logger.info(f"WebScraper: Starting web scraping for URL: {url}")
        
        try:
            # Create async client
            async with httpx.AsyncClient(verify=False, timeout=30) as client:
                logger.info("WebScraper: Connecting to website...")
                
                # Fetch the webpage
                response = await client.get(url)
                response.raise_for_status()
                
                logger.info("WebScraper: Successfully connected to website")
                
                # Parse HTML content
                logger.info("WebScraper: Parsing HTML content...")
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info("WebScraper: HTML content parsed successfully")
                
                # Extract product data
                logger.info("WebScraper: Extracting product title...")
                title = self._extract_title(soup)
                logger.info(f"WebScraper: Title extracted: {title[:50]}...")
                
                logger.info("WebScraper: Extracting product description...")
                description = self._extract_description(soup)
                logger.info(f"WebScraper: Description extracted: {description[:50]}...")
                
                logger.info("WebScraper: Extracting product price...")
                price = self._extract_price(soup)
                logger.info(f"WebScraper: Price extracted: {price}")
                
                logger.info("WebScraper: Extracting product images...")
                images = self._extract_images(soup, url)
                logger.info(f"WebScraper: Found {len(images)} images")
                
                logger.info("WebScraper: Extracting product features...")
                features = self._extract_features(soup)
                logger.info(f"WebScraper: Found {len(features)} features")
                
                logger.info("WebScraper: Product data extraction completed successfully!")
                
                return ProductData(
                    title=title,
                    description=description,
                    price=price,
                    images=images,
                    features=features
                )
                
        except Exception as e:
            logger.error(f"WebScraper: Failed to extract data from {url}: {str(e)}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title from the page"""
        # Try multiple selectors for title
        title_selectors = [
            'h1[class*="title"]',
            'h1[class*="product"]',
            'h1[class*="name"]',
            'h1',
            '[class*="title"]',
            '[class*="product-name"]',
            '[class*="product-title"]',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                title = element.get_text().strip()
                if len(title) > 10 and len(title) < 200:
                    return title
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        return "Product"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description from the page"""
        # Try multiple selectors for description
        desc_selectors = [
            '[class*="description"]',
            '[class*="product-description"]',
            '[class*="product-details"]',
            '[class*="details"]',
            'p[class*="description"]',
            'div[class*="description"]',
            'meta[name="description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if selector == 'meta[name="description"]':
                    desc = element.get('content', '')
                else:
                    desc = element.get_text().strip()
                
                if desc and len(desc) > 20:
                    return desc[:500]  # Limit description length
        
        return "High-quality product with excellent features."
    
    def _extract_price(self, soup: BeautifulSoup) -> str:
        """Extract product price from the page"""
        # Try multiple selectors for price
        price_selectors = [
            '[class*="price"]',
            '[class*="cost"]',
            '[class*="amount"]',
            'span[class*="price"]',
            'div[class*="price"]',
            '[data-price]',
            '[itemprop="price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text().strip()
                # Extract price using regex
                price_match = re.search(r'[\$£€]?\s*\d+\.?\d*', price_text)
                if price_match:
                    return price_match.group()
        
        return "Check price"
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract product images from the page"""
        images = []
        img_tags = soup.find_all('img')
        
        # Filter and prioritize images
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not src:
                continue
            
            # Make URL absolute
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(base_url, src)
            elif not src.startswith('http'):
                src = urljoin(base_url, src)
            
            # Skip certain image types
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(base_url, src)
            elif not src.startswith('http'):
                src = urljoin(base_url, src)

            # ⛔️ Exclude unsupported file types early
            if src.lower().endswith(('.svg', '.gif', '.webp')):
                logger.debug(f"WebScraper: Excluded unsupported image format: {src}")
                continue
            UNWANTED_PATTERNS = [
                'logo', 'icon', 'banner', 'ad', 'tracking', 'pixel',
                'analytics', 'social', 'share', 'avatar', 'profile',
                'thumb', 'placeholder', 'flag', 'country'
            ]

            if any(pat in src.lower() for pat in UNWANTED_PATTERNS):
                logger.debug(f"WebScraper: Excluded image (pattern match): {src}")
                continue
            # Get image dimensions
            width = img.get('width', 0)
            height = img.get('height', 0)
            
            # Try to get dimensions from style attribute
            style = img.get('style', '')
            if style:
                width_match = re.search(r'width:\s*(\d+)px', style)
                height_match = re.search(r'height:\s*(\d+)px', style)
                if width_match:
                    width = int(width_match.group(1))
                if height_match:
                    height = int(height_match.group(1))
            
            # Skip very small images
            if width and height and (width < 100 or height < 100):
                logger.debug(f"WebScraper: Excluded image (too small): {src} ({width}x{height})")
                continue
            
            # Special handling for Amazon
            if 'amazon' in base_url.lower():
                if 'data-old-hires' in img.attrs:
                    src = img['data-old-hires']
                elif 'data-a-dynamic-image' in img.attrs:
                    # Parse dynamic image JSON
                    try:
                        import json
                        dynamic_data = json.loads(img['data-a-dynamic-image'])
                        if dynamic_data:
                            # Get the largest image
                            largest_url = max(dynamic_data.keys(), key=lambda x: dynamic_data[x][0])
                            src = largest_url
                    except:
                        pass
                
                # Filter Amazon-specific images
                if 'sprite' in src.lower() or 'transparent' in src.lower():
                    logger.debug(f"WebScraper: Excluded tiny Amazon icon: {src}")
                    continue
                
                # Prioritize large Amazon product images
                if 'images-na.ssl-images-amazon.com' in src and ('L.' in src or 'SX' in src):
                    if 'L.' in src:
                        logger.debug(f"WebScraper: Added large Amazon product image: {src}")
                        images.insert(0, src)  # Add to beginning
                    elif 'SX' in src:
                        logger.debug(f"WebScraper: Added medium Amazon product image: {src}")
                        images.append(src)
                    else:
                        logger.debug(f"WebScraper: Added Amazon product image: {src}")
                        images.append(src)
                else:
                    logger.debug(f"WebScraper: Excluded non-product Amazon image: {src}")
                    continue
            else:
                # For non-Amazon sites, be more lenient
                if width and height and width > 200 and height > 200:
                    logger.debug(f"WebScraper: Added product image: {src}")
                    images.append(src)
                else:
                    logger.debug(f"WebScraper: Added potential product image: {src}")
                    images.append(src)
        
        # Remove duplicates and limit to 20 images
        # Remove duplicates and limit to 20 images
        unique_images = list(dict.fromkeys(images))
        best_images = unique_images[:20]  # Always assign, even if fewer than 20

        logger.info(f"WebScraper: Found {len(best_images)} product images out of {len(img_tags)} total images")
        return best_images
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features from the page"""
        features = []
        
        # Try multiple selectors for features
        feature_selectors = [
            '[class*="feature"]',
            '[class*="benefit"]',
            '[class*="specification"]',
            '[class*="spec"]',
            'li[class*="feature"]',
            'li[class*="benefit"]',
            'ul[class*="feature"] li',
            'ul[class*="benefit"] li',
            'ul[class*="spec"] li'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and len(text) > 10 and len(text) < 200:
                    # Clean up the text
                    text = re.sub(r'\s+', ' ', text)
                    if text not in features:
                        features.append(text)
        
        # If no features found, try to extract from bullet points
        if not features:
            bullet_points = soup.find_all(['li', 'p'])
            for point in bullet_points:
                text = point.get_text().strip()
                if text and len(text) > 10 and len(text) < 200:
                    # Check if it looks like a feature
                    if any(word in text.lower() for word in ['feature', 'benefit', 'advantage', 'include', 'comes with']):
                        text = re.sub(r'\s+', ' ', text)
                        if text not in features:
                            features.append(text)
        
        return features[:10]  # Limit to 10 features 