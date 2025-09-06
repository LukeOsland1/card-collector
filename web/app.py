"""FastAPI web application."""
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from db.database import get_db_session, init_database, close_database, get_database_health
from db.config import is_mongodb
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

# Database lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_database()
    logger.info("Database initialized")


@app.on_event("shutdown") 
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_database()
    logger.info("Database connections closed")


# Include API routes
app.include_router(api_router)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request, 
    current_user: Optional[dict] = Depends(optional_auth),
    error: Optional[str] = None
):
    """Home page."""
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": current_user,
            "error": error,
        }
    )


@app.get("/login")
async def login(request: Request, state: Optional[str] = None):
    """Redirect to Discord OAuth."""
    oauth_url = get_discord_oauth_url(state)
    return RedirectResponse(url=oauth_url)


@app.get("/logout")
async def logout():
    """Handle user logout."""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@app.get("/debug/test-login")
async def test_login(request: Request, db = Depends(get_db_session)):
    """Debug endpoint to test cookie authentication locally."""
    import os
    if os.getenv("DEBUG", "false").lower() != "true":
        raise HTTPException(status_code=404, detail="Not found")
    
    from .auth import create_access_token
    from db.database import UserCRUD
    
    test_discord_id = 123456789
    
    # Create or get test user in database
    test_user = await UserCRUD.get_or_create(db, test_discord_id)
    
    # Create a test token
    test_token = create_access_token({
        "discord_id": test_discord_id,
        "username": "TestUser#0001"
    })
    
    # Create response with cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    is_secure = request.url.scheme == "https"
    response.set_cookie(
        key="access_token",
        value=test_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=30 * 60,
    )
    
    return response


@app.get("/auth/callback")
async def auth_callback(
    code: str,
    state: Optional[str] = None,
    db = Depends(get_db_session),
):
    """Handle Discord OAuth callback."""
    try:
        login_result = await login_with_discord(code, db)
        
        # Create a redirect response to the homepage
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
        # Set JWT token as HTTP-only cookie for security
        # In development (HTTP), secure=False; in production (HTTPS), secure=True
        is_secure = request.url.scheme == "https"
        response.set_cookie(
            key="access_token",
            value=login_result["access_token"],
            httponly=True,
            secure=is_secure,  # Use HTTPS in production only
            samesite="lax",
            max_age=30 * 60,  # 30 minutes to match JWT expiry
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        # Redirect to home with error parameter
        return RedirectResponse(url="/?error=login_failed", status_code=status.HTTP_302_FOUND)


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


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: Optional[dict] = Depends(optional_auth)
):
    """Card upload page."""
    return templates.TemplateResponse(
        "upload.html",
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
    db_health = await get_database_health()
    return {
        "status": "ok", 
        "service": "card-collector-web",
        "database": db_health,
        "database_type": "mongodb" if is_mongodb() else "sql"
    }


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