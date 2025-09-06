"""Image processing and CDN handling for card attachments."""
import asyncio
import io
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import discord
import httpx
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FORMATS = {'PNG', 'JPEG', 'JPG', 'WEBP', 'GIF'}
MAX_IMAGE_DIMENSION = 2048
THUMBNAIL_SIZE = (256, 256)

# CDN configuration (you would set this based on your setup)
CDN_UPLOAD_URL = os.getenv("CDN_UPLOAD_URL", "")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "")
CDN_API_KEY = os.getenv("CDN_API_KEY", "")


async def validate_image_attachment(attachment: discord.Attachment) -> Tuple[bool, str]:
    """
    Validate an image attachment.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check file size
    if attachment.size > MAX_FILE_SIZE:
        size_mb = attachment.size / (1024 * 1024)
        return False, f"File too large ({size_mb:.1f}MB). Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB."
    
    # Check file extension
    file_ext = attachment.filename.split('.')[-1].upper()
    if file_ext not in ALLOWED_FORMATS:
        return False, f"Invalid file format. Allowed formats: {', '.join(ALLOWED_FORMATS)}"
    
    # Check if it's actually an image by trying to read it
    try:
        image_data = await attachment.read()
        with Image.open(io.BytesIO(image_data)) as img:
            # Verify it's a valid image
            img.verify()
            
            # Reopen for dimension check (verify() closes the image)
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                return False, f"Image too large ({width}x{height}). Maximum dimension is {MAX_IMAGE_DIMENSION}px."
                
            if width < 64 or height < 64:
                return False, f"Image too small ({width}x{height}). Minimum dimension is 64px."
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validating image: {e}")
        return False, "Invalid or corrupted image file."


async def process_image_attachment(
    attachment: discord.Attachment, 
    rarity = None, 
    card_name: str = ""
) -> Tuple[str, str]:
    """
    Process an image attachment and return URLs for the full image and thumbnail.
    
    Returns:
        Tuple[str, str]: (image_url, thumbnail_url)
    """
    # Use the new image service if rarity is provided
    if rarity:
        from services.image_service import process_discord_attachment
        try:
            results = await process_discord_attachment(attachment, rarity, card_name)
            return results.get("image_url", ""), results.get("thumb_url", "")
        except ImportError:
            pass  # Fall back to original implementation
    
    # Original implementation as fallback
    image_data = await attachment.read()
    processed_image, thumbnail_image = await _process_images(image_data)
    
    if CDN_UPLOAD_URL and CDN_API_KEY:
        image_url = await _upload_to_cdn(processed_image, attachment.filename, "image")
        thumb_url = await _upload_to_cdn(thumbnail_image, f"thumb_{attachment.filename}", "thumbnail")
    else:
        image_url = await _save_locally(processed_image, attachment.filename, "image")
        thumb_url = await _save_locally(thumbnail_image, f"thumb_{attachment.filename}", "thumbnail")
    
    return image_url, thumb_url


async def _process_images(image_data: bytes) -> Tuple[bytes, bytes]:
    """Process image data to create full image and thumbnail."""
    
    def _process_sync():
        """Synchronous image processing function."""
        # Load image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
        
        # Save processed full image
        full_buffer = io.BytesIO()
        img.save(full_buffer, format='JPEG', quality=90, optimize=True)
        full_image_data = full_buffer.getvalue()
        
        # Create thumbnail
        thumb_img = img.copy()
        thumb_img = ImageOps.fit(thumb_img, THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        
        thumb_buffer = io.BytesIO()
        thumb_img.save(thumb_buffer, format='JPEG', quality=85, optimize=True)
        thumb_image_data = thumb_buffer.getvalue()
        
        return full_image_data, thumb_image_data
    
    # Run image processing in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_sync)


async def _upload_to_cdn(image_data: bytes, filename: str, image_type: str) -> str:
    """Upload image to CDN service."""
    try:
        # This is a generic CDN upload implementation
        # You would customize this based on your CDN provider (AWS S3, Cloudinary, etc.)
        
        headers = {
            "Authorization": f"Bearer {CDN_API_KEY}",
            "Content-Type": "multipart/form-data"
        }
        
        files = {
            "file": (filename, image_data, "image/jpeg"),
            "folder": image_type,  # Organize by type
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(CDN_UPLOAD_URL, headers=headers, files=files)
            response.raise_for_status()
            
            result = response.json()
            return result.get("url", "")
            
    except Exception as e:
        logger.error(f"Error uploading to CDN: {e}")
        # Fallback to local storage
        return await _save_locally(image_data, filename, image_type)


async def _save_locally(image_data: bytes, filename: str, image_type: str) -> str:
    """Save image to local storage as fallback."""
    try:
        # Create directories
        storage_dir = Path("storage") / "images" / image_type
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        if not unique_filename.lower().endswith(('.jpg', '.jpeg')):
            unique_filename += '.jpg'
        
        file_path = storage_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Return relative URL (you'd serve these via your web server)
        return f"/static/images/{image_type}/{unique_filename}"
        
    except Exception as e:
        logger.error(f"Error saving image locally: {e}")
        raise


async def download_and_process_url(image_url: str) -> Tuple[str, str]:
    """Download image from URL and process it."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            
            image_data = response.content
            
            # Validate the downloaded image
            with Image.open(io.BytesIO(image_data)) as img:
                img.verify()
            
            # Process the image
            processed_image, thumbnail_image = await _process_images(image_data)
            
            # Generate filename from URL
            filename = image_url.split('/')[-1] or 'image.jpg'
            
            # Upload processed images
            if CDN_UPLOAD_URL and CDN_API_KEY:
                image_url = await _upload_to_cdn(processed_image, filename, "image")
                thumb_url = await _upload_to_cdn(thumbnail_image, f"thumb_{filename}", "thumbnail")
            else:
                image_url = await _save_locally(processed_image, filename, "image")
                thumb_url = await _save_locally(thumbnail_image, f"thumb_{filename}", "thumbnail")
            
            return image_url, thumb_url
            
    except Exception as e:
        logger.error(f"Error downloading and processing image from URL: {e}")
        raise


def get_image_info(image_data: bytes) -> dict:
    """Get information about an image."""
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
            }
    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        return {}


async def create_card_preview(
    image_data: bytes,
    card_name: str,
    rarity: str,
    description: Optional[str] = None
) -> bytes:
    """Create a stylized card preview (optional feature)."""
    
    def _create_preview_sync():
        """Synchronous preview creation."""
        # Load the card image
        card_img = Image.open(io.BytesIO(image_data))
        
        # Create card template (this is a simple example)
        # You could create more elaborate card designs
        card_width, card_height = 400, 600
        preview = Image.new('RGB', (card_width, card_height), (255, 255, 255))
        
        # Resize and center the image
        img_height = 350
        card_img.thumbnail((card_width - 40, img_height), Image.Resampling.LANCZOS)
        img_x = (card_width - card_img.width) // 2
        img_y = 20
        
        preview.paste(card_img, (img_x, img_y))
        
        # You would add text rendering here using PIL's ImageDraw
        # For now, this is just a placeholder
        
        # Save as bytes
        buffer = io.BytesIO()
        preview.save(buffer, format='PNG', optimize=True)
        return buffer.getvalue()
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _create_preview_sync)


async def cleanup_orphaned_images():
    """Clean up images that are no longer referenced in the database."""
    # This would be run as a background task
    # Implementation would check the database for referenced images
    # and remove any files that are no longer needed
    pass


def is_animated_gif(image_data: bytes) -> bool:
    """Check if image data is an animated GIF."""
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            return getattr(img, "is_animated", False)
    except Exception:
        return False


async def extract_gif_frames(image_data: bytes, max_frames: int = 10) -> list[bytes]:
    """Extract frames from animated GIF for preview."""
    
    def _extract_frames_sync():
        frames = []
        with Image.open(io.BytesIO(image_data)) as img:
            for i in range(min(img.n_frames, max_frames)):
                img.seek(i)
                frame = img.copy()
                if frame.mode != 'RGB':
                    frame = frame.convert('RGB')
                
                buffer = io.BytesIO()
                frame.save(buffer, format='JPEG', quality=80)
                frames.append(buffer.getvalue())
                
        return frames
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_frames_sync)