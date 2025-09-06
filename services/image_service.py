"""Advanced image processing and storage service."""
import asyncio
import io
import logging
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import aiofiles
import httpx
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from PIL.ExifTags import ORIENTATION

from db.models import CardRarity

logger = logging.getLogger(__name__)

# Configuration
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", "90"))
THUMBNAIL_SIZE = (256, 256)
PREVIEW_SIZE = (512, 512)
MAX_IMAGE_SIZE = (2048, 2048)
WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "")

# Rarity color schemes
RARITY_COLORS = {
    CardRarity.COMMON: "#95a5a6",      # Gray
    CardRarity.UNCOMMON: "#2ecc71",    # Green  
    CardRarity.RARE: "#3498db",        # Blue
    CardRarity.EPIC: "#9b59b6",        # Purple
    CardRarity.LEGENDARY: "#f39c12",   # Gold
}

RARITY_GRADIENTS = {
    CardRarity.COMMON: ["#95a5a6", "#7f8c8d"],
    CardRarity.UNCOMMON: ["#2ecc71", "#27ae60"],
    CardRarity.RARE: ["#3498db", "#2980b9"],
    CardRarity.EPIC: ["#9b59b6", "#8e44ad"],
    CardRarity.LEGENDARY: ["#f39c12", "#e67e22"],
}


class ImageProcessor:
    """Advanced image processing service."""
    
    def __init__(self):
        self.storage_path = STORAGE_PATH
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories."""
        directories = [
            self.storage_path / "images",
            self.storage_path / "thumbnails", 
            self.storage_path / "previews",
            self.storage_path / "cards",
            self.storage_path / "temp",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def process_card_image(
        self,
        image_data: bytes,
        filename: str,
        rarity: CardRarity,
        card_name: str = "",
        create_card_preview: bool = True,
    ) -> Dict[str, str]:
        """
        Process a card image and generate all required variants.
        
        Returns:
            Dict with URLs for different image variants
        """
        try:
            # Generate unique filename
            file_hash = hashlib.md5(image_data).hexdigest()
            timestamp = int(datetime.utcnow().timestamp())
            base_name = f"{file_hash}_{timestamp}"
            
            # Process original image
            processed_image = await self._process_original_image(image_data)
            
            # Generate variants
            results = {}
            
            # Save original processed image
            original_path = await self._save_image(
                processed_image, 
                self.storage_path / "images" / f"{base_name}.jpg"
            )
            results["image_url"] = self._get_url(original_path)
            
            # Generate thumbnail
            thumbnail = await self._create_thumbnail(processed_image)
            thumbnail_path = await self._save_image(
                thumbnail,
                self.storage_path / "thumbnails" / f"{base_name}_thumb.jpg"
            )
            results["thumb_url"] = self._get_url(thumbnail_path)
            
            # Generate preview
            preview = await self._create_preview(processed_image, rarity)
            preview_path = await self._save_image(
                preview,
                self.storage_path / "previews" / f"{base_name}_preview.jpg"
            )
            results["preview_url"] = self._get_url(preview_path)
            
            # Generate card-style image if requested
            if create_card_preview:
                card_image = await self._create_card_style(
                    processed_image, card_name, rarity
                )
                card_path = await self._save_image(
                    card_image,
                    self.storage_path / "cards" / f"{base_name}_card.jpg"
                )
                results["card_url"] = self._get_url(card_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing card image: {e}")
            raise
    
    async def _process_original_image(self, image_data: bytes) -> Image.Image:
        """Process the original image."""
        def _process_sync():
            # Load image
            img = Image.open(io.BytesIO(image_data))
            
            # Handle EXIF rotation
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                if ORIENTATION in exif:
                    orientation = exif[ORIENTATION]
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > MAX_IMAGE_SIZE[0] or img.height > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Apply minor sharpening
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            return img
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _process_sync)
    
    async def _create_thumbnail(self, img: Image.Image) -> Image.Image:
        """Create a thumbnail image."""
        def _create_sync():
            # Create thumbnail using smart cropping
            thumbnail = ImageOps.fit(
                img, THUMBNAIL_SIZE, Image.Resampling.LANCZOS, centering=(0.5, 0.5)
            )
            
            # Apply slight sharpening to thumbnail
            thumbnail = thumbnail.filter(
                ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3)
            )
            
            return thumbnail
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_sync)
    
    async def _create_preview(
        self, img: Image.Image, rarity: CardRarity
    ) -> Image.Image:
        """Create a preview image with rarity border."""
        def _create_sync():
            # Create preview size image
            preview = ImageOps.fit(
                img, PREVIEW_SIZE, Image.Resampling.LANCZOS, centering=(0.5, 0.5)
            )
            
            # Add rarity border
            border_size = 8
            rarity_color = RARITY_COLORS[rarity]
            
            # Create border
            bordered = ImageOps.expand(
                preview, border=border_size, fill=rarity_color
            )
            
            # Add inner shadow effect
            shadow = Image.new('RGBA', bordered.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(shadow)
            
            # Draw gradient border effect
            for i in range(border_size // 2):
                alpha = int(255 * (1 - i / (border_size // 2)))
                draw.rectangle([
                    i, i, 
                    bordered.width - i - 1, 
                    bordered.height - i - 1
                ], outline=(*self._hex_to_rgb(rarity_color), alpha))
            
            # Composite shadow onto bordered image
            bordered = Image.alpha_composite(
                bordered.convert('RGBA'), shadow
            ).convert('RGB')
            
            return bordered
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_sync)
    
    async def _create_card_style(
        self, img: Image.Image, card_name: str, rarity: CardRarity
    ) -> Image.Image:
        """Create a trading card style image."""
        def _create_sync():
            # Card dimensions (portrait orientation)
            card_width, card_height = 400, 600
            
            # Create card background
            card = Image.new('RGB', (card_width, card_height), (255, 255, 255))
            draw = ImageDraw.Draw(card)
            
            # Create gradient background
            gradient_colors = RARITY_GRADIENTS[rarity]
            for y in range(card_height):
                ratio = y / card_height
                color = self._interpolate_color(
                    self._hex_to_rgb(gradient_colors[0]),
                    self._hex_to_rgb(gradient_colors[1]),
                    ratio
                )
                draw.line([(0, y), (card_width, y)], fill=color)
            
            # Add image area (top portion)
            image_height = int(card_height * 0.6)
            image_margin = 20
            image_area = (
                image_margin,
                image_margin, 
                card_width - image_margin,
                image_height
            )
            
            # Resize and paste card image
            card_img = img.copy()
            card_img.thumbnail(
                (image_area[2] - image_area[0], image_area[3] - image_area[1]),
                Image.Resampling.LANCZOS
            )
            
            # Center the image
            img_x = image_area[0] + (image_area[2] - image_area[0] - card_img.width) // 2
            img_y = image_area[1] + (image_area[3] - image_area[1] - card_img.height) // 2
            
            card.paste(card_img, (img_x, img_y))
            
            # Add decorative border around image
            border_color = self._hex_to_rgb(RARITY_COLORS[rarity])
            draw.rectangle([
                img_x - 3, img_y - 3,
                img_x + card_img.width + 3,
                img_y + card_img.height + 3
            ], outline=border_color, width=3)
            
            # Add card name
            if card_name:
                try:
                    # Try to load a nice font
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                
                # Calculate text position
                text_y = image_height + 30
                
                # Add text shadow
                draw.text((52, text_y + 2), card_name, fill=(0, 0, 0, 128), font=font)
                # Add main text
                draw.text((50, text_y), card_name, fill=(255, 255, 255), font=font)
            
            # Add rarity indicator
            rarity_text = rarity.value.upper()
            try:
                rarity_font = ImageFont.truetype("arial.ttf", 16)
            except:
                rarity_font = ImageFont.load_default()
            
            rarity_y = card_height - 50
            draw.text((52, rarity_y + 1), rarity_text, fill=(0, 0, 0, 128), font=rarity_font)
            draw.text((50, rarity_y), rarity_text, fill=(255, 255, 255), font=rarity_font)
            
            # Add corner decorations
            corner_size = 30
            corner_color = border_color
            
            # Top corners
            draw.polygon([
                (0, 0), (corner_size, 0), (0, corner_size)
            ], fill=corner_color)
            draw.polygon([
                (card_width, 0), (card_width - corner_size, 0), (card_width, corner_size)
            ], fill=corner_color)
            
            # Bottom corners  
            draw.polygon([
                (0, card_height), (corner_size, card_height), (0, card_height - corner_size)
            ], fill=corner_color)
            draw.polygon([
                (card_width, card_height), (card_width - corner_size, card_height), 
                (card_width, card_height - corner_size)
            ], fill=corner_color)
            
            return card
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_sync)
    
    async def _save_image(self, img: Image.Image, path: Path) -> Path:
        """Save image to disk asynchronously."""
        def _save_sync():
            with io.BytesIO() as buffer:
                img.save(buffer, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
                return buffer.getvalue()
        
        loop = asyncio.get_event_loop()
        image_data = await loop.run_in_executor(None, _save_sync)
        
        async with aiofiles.open(path, 'wb') as f:
            await f.write(image_data)
        
        return path
    
    def _get_url(self, path: Path) -> str:
        """Convert file path to URL."""
        # In production, this would return the full URL
        # For now, return a relative path
        relative_path = path.relative_to(self.storage_path)
        return f"/static/{relative_path}"
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _interpolate_color(
        self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float
    ) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * ratio) 
            for i in range(3)
        )
    
    async def create_collage(
        self, images: List[Image.Image], grid_size: Tuple[int, int] = (3, 3)
    ) -> Image.Image:
        """Create a collage from multiple images."""
        def _create_collage_sync():
            cols, rows = grid_size
            if len(images) > cols * rows:
                images = images[:cols * rows]
            
            # Calculate cell size
            cell_width = 200
            cell_height = 200
            
            # Create collage canvas
            collage_width = cols * cell_width
            collage_height = rows * cell_height
            collage = Image.new('RGB', (collage_width, collage_height), (240, 240, 240))
            
            for i, img in enumerate(images):
                row = i // cols
                col = i % cols
                
                # Resize image to fit cell
                cell_img = ImageOps.fit(
                    img, (cell_width - 10, cell_height - 10), Image.Resampling.LANCZOS
                )
                
                # Calculate position
                x = col * cell_width + 5
                y = row * cell_height + 5
                
                # Paste image
                collage.paste(cell_img, (x, y))
            
            return collage
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_collage_sync)
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours."""
        try:
            temp_dir = self.storage_path / "temp"
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            for file_path in temp_dir.glob("*"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        logger.info(f"Cleaned up temp file: {file_path}")
        
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    async def get_image_stats(self) -> Dict[str, any]:
        """Get statistics about stored images."""
        try:
            stats = {
                "total_images": 0,
                "total_thumbnails": 0,
                "total_previews": 0,
                "total_cards": 0,
                "total_size_mb": 0,
                "directories": {}
            }
            
            for directory in ["images", "thumbnails", "previews", "cards"]:
                dir_path = self.storage_path / directory
                file_count = len(list(dir_path.glob("*")))
                
                # Calculate directory size
                total_size = sum(f.stat().st_size for f in dir_path.glob("*") if f.is_file())
                
                stats[f"total_{directory}"] = file_count
                stats["directories"][directory] = {
                    "count": file_count,
                    "size_mb": round(total_size / 1024 / 1024, 2)
                }
                stats["total_size_mb"] += total_size / 1024 / 1024
            
            stats["total_size_mb"] = round(stats["total_size_mb"], 2)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting image stats: {e}")
            return {"error": str(e)}


# Global image processor instance
image_processor = ImageProcessor()


async def process_discord_attachment(
    attachment, rarity: CardRarity, card_name: str = ""
) -> Dict[str, str]:
    """Process a Discord attachment and return image URLs."""
    try:
        # Download attachment
        image_data = await attachment.read()
        
        # Process the image
        results = await image_processor.process_card_image(
            image_data=image_data,
            filename=attachment.filename,
            rarity=rarity,
            card_name=card_name,
            create_card_preview=True,
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing Discord attachment: {e}")
        raise


async def process_url_image(
    image_url: str, rarity: CardRarity, card_name: str = ""
) -> Dict[str, str]:
    """Process an image from a URL."""
    try:
        # Download image from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=30.0)
            response.raise_for_status()
            image_data = response.content
        
        # Extract filename from URL
        filename = image_url.split('/')[-1] or 'image.jpg'
        
        # Process the image
        results = await image_processor.process_card_image(
            image_data=image_data,
            filename=filename,
            rarity=rarity,
            card_name=card_name,
            create_card_preview=True,
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing URL image: {e}")
        raise