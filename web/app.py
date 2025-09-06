"""FastAPI web application."""
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import get_db
from .api import router as api_router
from .auth import get_discord_oauth_url, login_with_discord, optional_auth

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Card Collector API",
    description="API and web interface for the Card Collector Discord bot",
    version="1.0.0"
)

# Configure CORS based on environment
import os
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if DEBUG:
    # Development: Allow all origins
    cors_origins = ["*"]
else:
    # Production: Restrict to specific domains
    cors_origins = [
        "https://your-domain.com",
        "https://www.your-domain.com",
        # Add your actual production domains here
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    current_user: Optional[dict] = Depends(optional_auth)
):
    """Home page."""
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": current_user,
        }
    )


@app.get("/login")
async def login(request: Request, state: Optional[str] = None):
    """Redirect to Discord OAuth."""
    oauth_url = get_discord_oauth_url(state)
    return RedirectResponse(url=oauth_url)


@app.get("/auth/callback")
async def auth_callback(
    code: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Handle Discord OAuth callback."""
    try:
        login_result = await login_with_discord(code, db)
        
        # In a real app, you'd set an HTTP-only cookie here
        # For now, return the token (client should handle this securely)
        return {
            "status": "success",
            "access_token": login_result["access_token"],
            "user": login_result["user"]
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed"
        )


@app.get("/cards", response_class=HTMLResponse)
async def cards_page(
    request: Request,
    current_user: Optional[dict] = Depends(optional_auth)
):
    """Cards browse page."""
    return templates.TemplateResponse(
        "cards.html",
        {
            "request": request,
            "user": current_user,
        }
    )


@app.get("/collection", response_class=HTMLResponse)
async def collection_page(
    request: Request,
    current_user: Optional[dict] = Depends(optional_auth)
):
    """User collection page."""
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse(
        "collection.html",
        {
            "request": request,
            "user": current_user,
        }
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    current_user: Optional[dict] = Depends(optional_auth)
):
    """Admin dashboard page."""
    if not current_user or not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": current_user,
        }
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "card-collector-web"}


if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "8080"))
    
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Card Collector Web Server...")
    
    uvicorn.run(
        "web.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )