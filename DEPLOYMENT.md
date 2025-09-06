# Deployment Guide

This guide covers deploying the Card Collector web application to various hosting platforms.

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Prerequisites:**
   ```bash
   # Install Docker and Docker Compose
   # https://docs.docker.com/get-docker/
   ```

2. **Deploy:**
   ```bash
   # Clone the repository
   git clone https://github.com/YourUsername/card-collector.git
   cd card-collector
   
   # Set environment variables
   cp env.example .env
   # Edit .env with your Discord bot credentials
   
   # Deploy with SQLite (simpler)
   docker-compose up -d web
   
   # OR Deploy with PostgreSQL (production)
   docker-compose --profile postgres up -d
   ```

3. **Access:**
   - Web App: http://localhost:8080
   - API Docs: http://localhost:8080/docs
   - Admin Panel (optional): http://localhost:8081

## ☁️ Cloud Platform Deployment

### Heroku

1. **Prerequisites:**
   ```bash
   # Install Heroku CLI
   # https://devcenter.heroku.com/articles/heroku-cli
   heroku login
   ```

2. **Deploy:**
   ```bash
   # Create Heroku app
   heroku create your-card-collector-app
   
   # Set environment variables
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   heroku config:set JWT_SECRET_KEY=$(openssl rand -base64 32)
   heroku config:set DATABASE_URL=sqlite+aiosqlite:///./card_collector.db
   
   # Deploy
   git push heroku main
   ```

3. **Custom Domain (optional):**
   ```bash
   heroku domains:add your-domain.com
   # Configure DNS to point to Heroku
   ```

### DigitalOcean App Platform

1. **Create `app.yaml`:**
   ```yaml
   name: card-collector
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/card-collector
       branch: main
     run_command: python -m uvicorn web.app:app --host 0.0.0.0 --port 8080
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     http_port: 8080
     health_check:
       http_path: /api/health
     envs:
     - key: DISCORD_BOT_TOKEN
       scope: RUN_TIME
       type: SECRET
     - key: JWT_SECRET_KEY
       scope: RUN_TIME
       type: SECRET
     - key: DATABASE_URL
       value: sqlite+aiosqlite:///./card_collector.db
       scope: RUN_TIME
   ```

2. **Deploy:**
   ```bash
   # Using doctl CLI
   doctl apps create app.yaml
   
   # Or deploy via DigitalOcean web console
   # Upload your repository and configure environment variables
   ```

### AWS (Elastic Beanstalk)

1. **Create `requirements.txt` for EB:**
   ```bash
   # Already exists in the project
   ```

2. **Create `.ebextensions/python.config`:**
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: web.app:app
     aws:elasticbeanstalk:application:environment:
       PYTHONPATH: "/var/app/current"
   ```

3. **Deploy:**
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize and deploy
   eb init card-collector --platform python-3.11
   eb create card-collector-prod
   eb deploy
   ```

### Google Cloud Run

1. **Create `cloudbuild.yaml`:**
   ```yaml
   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/$PROJECT_ID/card-collector', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'gcr.io/$PROJECT_ID/card-collector']
   - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
     entrypoint: gcloud
     args: ['run', 'deploy', 'card-collector', '--image', 'gcr.io/$PROJECT_ID/card-collector', '--region', 'us-central1', '--platform', 'managed', '--allow-unauthenticated']
   ```

2. **Deploy:**
   ```bash
   # Enable required APIs
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   
   # Deploy
   gcloud builds submit --config cloudbuild.yaml
   ```

## 🔧 Configuration for Production

### Environment Variables

**Required:**
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
JWT_SECRET_KEY=your_jwt_secret_key
```

**Database (choose one):**
```env
# SQLite (simple, single instance)
DATABASE_URL=sqlite+aiosqlite:///./card_collector.db

# PostgreSQL (recommended for production)
DATABASE_URL=postgresql+psycopg://user:password@host:port/database
```

**Web Server:**
```env
WEB_HOST=0.0.0.0
WEB_PORT=8080
```

**Optional:**
```env
DEBUG=false
LOG_LEVEL=INFO
CDN_UPLOAD_URL=your_cdn_url
CDN_BASE_URL=your_cdn_base_url
CDN_API_KEY=your_cdn_api_key
```

### Security Considerations

1. **CORS Configuration:**
   ```python
   # Update web/app.py for production domains
   allow_origins=["https://your-domain.com"]
   ```

2. **JWT Secret:**
   ```bash
   # Generate secure JWT secret
   openssl rand -base64 64
   ```

3. **Discord OAuth:**
   ```
   # Update Discord app redirect URIs:
   https://your-domain.com/auth/callback
   ```

### Database Migration

For production PostgreSQL deployment:

```bash
# Set DATABASE_URL to PostgreSQL
export DATABASE_URL="postgresql+psycopg://user:password@host:port/database"

# Tables are created automatically on startup
python -c "from db.base import Base, async_engine; import asyncio; asyncio.run(Base.metadata.create_all(bind=async_engine))"
```

## 🚀 Performance Optimization

### Production Settings

```env
# Disable debug mode
DEBUG=false

# Set appropriate log level
LOG_LEVEL=WARNING

# Configure worker processes (for Gunicorn)
WEB_WORKERS=4
WEB_WORKER_CLASS=uvicorn.workers.UvicornWorker
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files (if serving separately)
    location /static {
        alias /path/to/card-collector/web/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📊 Monitoring

### Health Checks

All platforms can use the built-in health endpoint:
```
GET /api/health
Response: {"status": "ok", "service": "card-collector-web"}
```

### Logging

The application logs to stdout/stderr by default. Configure your platform's logging aggregation:

- **Heroku:** `heroku logs --tail`
- **DigitalOcean:** Built-in log aggregation
- **AWS:** CloudWatch Logs
- **GCP:** Cloud Logging

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   ```bash
   # Check DATABASE_URL format
   # SQLite: sqlite+aiosqlite:///./database.db
   # PostgreSQL: postgresql+psycopg://user:pass@host:port/db
   ```

2. **Discord OAuth Issues:**
   ```bash
   # Verify redirect URI in Discord Developer Portal
   # Must match your deployed domain
   ```

3. **Static Files Not Loading:**
   ```bash
   # Check static file serving in production
   # Consider using CDN for static assets
   ```

4. **Memory Issues:**
   ```bash
   # Increase instance size/memory allocation
   # Monitor memory usage with your platform's tools
   ```

## 📞 Support

- **Documentation:** Check README.md for basic setup
- **Issues:** Report at GitHub Issues
- **Discord Setup:** See DISCORD_SETUP.md
- **Local Development:** Use `python run.py` for quick testing

## 🎉 Success!

Once deployed, you should see:
- ✅ Web interface accessible at your domain
- ✅ API documentation at `/docs`
- ✅ Health check returning `{"status": "ok"}`
- ✅ Discord bot responding to slash commands
- ✅ User authentication working via Discord OAuth

Your Card Collector is now live on the web! 🎴