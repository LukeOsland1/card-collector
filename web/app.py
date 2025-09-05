"""FastAPI web application."""
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Card Collector API",
    description="API and web interface for the Card Collector Discord bot",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="web/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "user": None,
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