# 🚀 Deployment Guide

This guide covers deploying Bright Ideas to various platforms.

## 🎯 Render (Recommended)

Render provides the easiest deployment with automatic builds and managed PostgreSQL.

### 1. Prerequisites
- **GitHub Account** with this repository
- **Render Account** (free tier available)
- **OpenAI API Key**

### 2. Setup Repository
```bash
# Fork or clone this repository
git clone <your-repository-url>
cd bright_ideas

# Ensure render.yaml is configured (already included)
```

### 3. Deploy on Render

#### Option A: One-Click Deploy
1. **Visit**: [Render Dashboard](https://dashboard.render.com)
2. **Click**: "New" → "Blueprint"
3. **Connect**: Your GitHub repository
4. **File**: `render.yaml` (auto-detected)
5. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key

#### Option B: Manual Service Creation
1. **Create Database**:
   - Name: `bright-ideas-db`
   - Database: `bright_ideas`
   - User: `bright_ideas_user`

2. **Create Backend Service**:
   - Type: Web Service
   - Runtime: Python 3
   - Build: `cd backend && pip install -r requirements.txt`
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_URL: <from database>
     OPENAI_API_KEY: <your key>
     ENVIRONMENT: production
     DEBUG: false
     CORS_ORIGINS: https://bright-ideas-frontend.onrender.com
     ```

3. **Create Frontend Service**:
   - Type: Web Service  
   - Runtime: Node.js
   - Build: `cd frontend && npm install && npm run build`
   - Start: `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     VITE_API_BASE_URL: https://bright-ideas-api.onrender.com
     ```

### 4. Post-Deployment
- **Run Migrations**: Access backend service shell and run `alembic upgrade head`
- **Test Application**: Visit your frontend URL
- **Update CORS**: Ensure backend CORS_ORIGINS includes your frontend domain

## 🐳 Docker Deployment

Deploy using Docker containers on any platform.

### 1. Build Images
```bash
# Build backend
cd backend
docker build -t bright-ideas-api .

# Build frontend  
cd frontend
docker build -t bright-ideas-frontend .
```

### 2. Deploy with Docker Compose
```bash
# Set environment variables
cp .env.example .env
# Edit .env with your values

# Start services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

### 3. Production Docker Setup
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bright_ideas
      POSTGRES_USER: bright_ideas_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    image: bright-ideas-api:latest
    environment:
      - DATABASE_URL=postgresql://bright_ideas_user:${DB_PASSWORD}@db:5432/bright_ideas
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db

  frontend:
    image: bright-ideas-frontend:latest
    environment:
      - VITE_API_BASE_URL=https://api.yourdomain.com
    ports:
      - "80:5173"

volumes:
  postgres_data:
```

## ☁️ Cloud Platforms

### AWS
1. **ECS/Fargate**: Deploy containers with RDS PostgreSQL
2. **Elastic Beanstalk**: Deploy backend with RDS  
3. **S3 + CloudFront**: Host frontend static files

### Google Cloud
1. **Cloud Run**: Deploy containerized services
2. **Cloud SQL**: Managed PostgreSQL database
3. **Cloud Storage**: Static frontend hosting

### Azure
1. **Container Instances**: Deploy containers
2. **Azure Database**: PostgreSQL service
3. **Static Web Apps**: Frontend hosting

## 🔧 Environment Configuration

### Backend Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/dbname
OPENAI_API_KEY=your_api_key

# Optional
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
API_PREFIX=/api/v1
```

### Frontend Environment Variables
```bash
# Required
VITE_API_BASE_URL=https://api.yourdomain.com

# Optional
VITE_APP_NAME="Bright Ideas"
VITE_ENABLE_ANALYTICS=false
```

## 🔍 Health Checks

### Backend Health Check
```bash
curl https://api.yourdomain.com/health
# Response: {"status": "healthy", "version": "1.0.0"}
```

### Database Health Check
```bash
# In backend container/environment
python -c "
from database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection: OK')
"
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
docker-compose logs api

# Common causes:
# 1. Missing OPENAI_API_KEY
# 2. Database connection issues
# 3. Port conflicts
```

#### Database Connection Errors
```bash
# Test connection
pg_isready -h hostname -p port -U username

# Check environment variables
echo $DATABASE_URL

# Run migrations
alembic upgrade head
```

#### Frontend Build Failures
```bash
# Clear cache
rm -rf node_modules .svelte-kit
npm install

# Check environment
echo $VITE_API_BASE_URL

# Test build
npm run build
```

#### CORS Errors
- **Backend**: Update `CORS_ORIGINS` in environment
- **Frontend**: Verify `VITE_API_BASE_URL` points to backend
- **Network**: Check firewall/proxy settings

### Performance Optimization

#### Backend
- **Gunicorn**: Use multiple workers in production
- **Caching**: Add Redis for API caching
- **Database**: Enable connection pooling

#### Frontend  
- **CDN**: Use CloudFront or similar for static assets
- **Compression**: Enable gzip/brotli compression
- **Caching**: Set appropriate cache headers

## 📊 Monitoring

### Application Metrics
- **Backend**: `/health` endpoint
- **Database**: Connection pool metrics
- **Frontend**: Core Web Vitals

### Logging
- **Backend**: Structured JSON logs
- **Database**: Query performance logs
- **Frontend**: Error tracking (Sentry, etc.)

### Alerts
- **Uptime**: Service availability monitoring
- **Errors**: 5xx error rate alerts
- **Performance**: Response time monitoring

## 🔐 Security

### Production Checklist
- [ ] **HTTPS**: SSL certificates configured
- [ ] **Environment Variables**: Secrets not in code
- [ ] **Database**: Connection encrypted
- [ ] **API Keys**: Properly secured
- [ ] **CORS**: Restricted to your domains
- [ ] **Updates**: Dependencies kept current

### Security Headers
```python
# backend/main.py additions
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
```

## 📈 Scaling

### Horizontal Scaling
- **Backend**: Multiple API instances behind load balancer
- **Database**: Read replicas for queries
- **Frontend**: CDN for global distribution

### Vertical Scaling
- **Memory**: Increase for large datasets
- **CPU**: More cores for concurrent requests
- **Storage**: SSD for database performance

---

**Need help?** [Open an issue](https://github.com/yourusername/bright-ideas/issues) or check the [discussions](https://github.com/yourusername/bright-ideas/discussions).