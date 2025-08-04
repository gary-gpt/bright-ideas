# 🛠️ Bright Ideas Development Manual

**Complete guide for developers working on the Bright Ideas project**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Deep Dive](#architecture-deep-dive)
3. [Development Environment Setup](#development-environment-setup)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Database Management](#database-management)
7. [API Development](#api-development)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Contributing Guidelines](#contributing-guidelines)

---

## 🎯 Project Overview

### Vision
Bright Ideas is an AI-powered brainstorming and planning tool that transforms vague concepts into actionable project plans through structured refinement and intelligent assistance.

### Core Features
- **Capture Mode**: Initial idea capture with AI-guided refinement
- **Build Mode**: Structured planning with AI collaboration
- **Export System**: Multi-format project documentation
- **Cross-Device**: Mobile-first responsive design

### Technical Stack
- **Backend**: FastAPI (Python) + PostgreSQL + OpenAI GPT-4o
- **Frontend**: SvelteKit + TypeScript + TailwindCSS
- **Deployment**: Render (Backend/DB) + Vercel/Netlify (Frontend)

---

## 🏗️ Architecture Deep Dive

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (SvelteKit)   │◄──►│   (FastAPI)     │◄──►│ (PostgreSQL)    │
│                 │    │                 │    │                 │
│ • Components    │    │ • API Routes    │    │ • Ideas         │
│ • Stores        │    │ • Services      │    │ • Conversations │
│ • Pages         │    │ • AI Integration│    │ • Build Plans   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   OpenAI API    │
                    │   (GPT-4o)      │
                    └─────────────────┘
```

### Data Flow
1. **User Input** → Frontend (SvelteKit)
2. **API Request** → Backend (FastAPI)
3. **Business Logic** → Services Layer
4. **AI Processing** → OpenAI GPT-4o
5. **Data Storage** → PostgreSQL
6. **Response** → Frontend → User

### Backend Architecture
```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration management
├── database.py          # SQLAlchemy setup
├── models.py            # Database models
├── schemas.py           # Pydantic validation
├── api/                 # Route handlers
│   ├── ideas.py
│   ├── conversations.py
│   └── planning.py
├── services/            # Business logic
│   ├── ai_service.py
│   ├── idea_service.py
│   ├── conversation_service.py
│   └── planning_service.py
└── alembic/             # Database migrations
```

### Frontend Architecture
```
frontend/src/
├── routes/              # SvelteKit pages
│   ├── +layout.svelte
│   ├── +page.svelte
│   ├── capture/
│   └── ideas/
├── lib/
│   ├── components/      # Reusable components
│   │   ├── shared/
│   │   ├── capture/
│   │   └── ideas/
│   ├── stores/          # State management
│   ├── services/        # API client
│   └── types/           # TypeScript definitions
└── app.html             # HTML template
```

---

## 💻 Development Environment Setup

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 13+**
- **Git** for version control
- **VS Code** (recommended) with extensions:
  - Python
  - Svelte for VS Code
  - Tailwind CSS IntelliSense
  - ESLint
  - Prettier

### Quick Setup
```bash
# 1. Clone repository
git clone <repository-url>
cd bright_ideas

# 2. Backend setup
make setup                    # Create virtual environment
source .venv/bin/activate    # Activate environment
make install-backend         # Install Python dependencies

# 3. Frontend setup
make install-frontend        # Install Node.js dependencies

# 4. Environment configuration
make env-setup              # Copy .env files
# Edit backend/.env and frontend/.env with your settings

# 5. Database setup
createdb bright_ideas       # Create PostgreSQL database
make db-migrate            # Run database migrations

# 6. Start development
make dev                   # Start both backend and frontend
```

### Environment Variables

#### Backend (`.env`)
```bash
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/bright_ideas
OPENAI_API_KEY=sk-your-api-key-here

# Optional
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]
API_PREFIX=/api/v1
```

#### Frontend (`.env`)
```bash
# Required
VITE_API_BASE_URL=http://localhost:8000

# Optional
VITE_APP_NAME="Bright Ideas"
VITE_ENABLE_DEBUG=true
```

### Development Workflow
```bash
# Daily workflow
git pull origin main
source .venv/bin/activate
make dev

# Testing
make test
make lint
make format

# Database changes
make db-revision MSG="Add new feature"
make db-migrate

# Production build
make build
make deploy-check
```

---

## 🐍 Backend Development

### FastAPI Application Structure

#### Main Application (`main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI(
    title="Bright Ideas API",
    description="AI-powered brainstorming tool",
    version="1.0.0"
)

# Middleware
app.add_middleware(CORSMiddleware, ...)

# Routes
app.include_router(ideas.router, prefix="/api/v1")
```

#### Configuration (`config.py`)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### Database Models (`models.py`)
```python
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    original_description = Column(Text, nullable=False)
    # ... other fields
```

### Service Layer Pattern

#### AI Service (`services/ai_service.py`)
```python
class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def refine_idea(self, description: str, history: List = None):
        # AI refinement logic
        response = await self.client.chat.completions.create(...)
        return structured_result

ai_service = AIService()
```

#### Business Logic Services
```python
class IdeaService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_idea(self, idea_data: IdeaCreate) -> Idea:
        db_idea = Idea(**idea_data.dict())
        self.db.add(db_idea)
        self.db.commit()
        return db_idea
```

### API Route Development

#### Route Structure
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/ideas", tags=["ideas"])

@router.post("/", response_model=IdeaResponse)
def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    service = IdeaService(db)
    return service.create_idea(idea)

@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: UUID, db: Session = Depends(get_db)):
    service = IdeaService(db)
    idea = service.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea
```

#### Error Handling
```python
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

### Database Operations

#### Migrations with Alembic
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

#### Complex Queries
```python
# Join queries
ideas_with_conversations = db.query(Idea)\
    .options(joinedload(Idea.conversations))\
    .filter(Idea.status == "refined")\
    .all()

# JSONB queries
plans_with_phases = db.query(BuildPlan)\
    .filter(BuildPlan.plan_data['phases'].astext.cast(Integer) > 3)\
    .all()
```

### Testing Backend

#### Unit Tests
```python
def test_create_idea():
    idea_data = IdeaCreate(
        title="Test Idea",
        original_description="Test description",
        tags=["test"]
    )
    service = IdeaService(db)
    result = service.create_idea(idea_data)
    assert result.title == "Test Idea"
```

#### API Tests
```python
def test_create_idea_endpoint():
    response = client.post("/api/v1/ideas", json={
        "title": "Test Idea",
        "original_description": "Test description"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Idea"
```

---

## ⚡ Frontend Development

### SvelteKit Application Structure

#### Route-Based Architecture
```
src/routes/
├── +layout.svelte          # Root layout
├── +page.svelte           # Dashboard
├── capture/
│   ├── +page.svelte       # Capture form
│   └── refine/[id]/
│       └── +page.svelte   # Refinement chat
└── ideas/
    ├── +page.svelte       # Ideas library
    └── [id]/
        └── +page.svelte   # Idea details
```

#### Component Development

##### Shared Components
```svelte
<!-- Button.svelte -->
<script lang="ts">
  export let variant: 'primary' | 'secondary' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled = false;
  export let loading = false;
  
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-secondary-600 hover:bg-secondary-700 text-white'
  };
  
  $: classes = `px-4 py-2 rounded-lg ${variants[variant]}`;
</script>

<button 
  class={classes}
  {disabled}
  on:click
>
  {#if loading}
    <LoadingSpinner size="sm" />
  {:else}
    <slot />
  {/if}
</button>
```

##### Feature Components
```svelte
<!-- IdeaCapture.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { IdeaCaptureForm } from '$types';
  
  const dispatch = createEventDispatcher<{ submit: IdeaCaptureForm }>();
  
  let form: IdeaCaptureForm = {
    title: '',
    description: '',
    tags: []
  };
  
  function handleSubmit() {
    if (isValid) {
      dispatch('submit', form);
    }
  }
  
  $: isValid = form.title.length > 0 && form.description.length >= 10;
</script>

<form on:submit|preventDefault={handleSubmit}>
  <!-- Form fields -->
</form>
```

### State Management with Stores

#### Svelte Stores Pattern
```typescript
// stores/ideas.ts
import { writable, derived } from 'svelte/store';
import type { Idea } from '$types';
import { api } from '$services/api';

// Store state
export const ideas = writable<Idea[]>([]);
export const currentIdea = writable<Idea | null>(null);
export const loading = writable(false);

// Derived stores
export const ideasByStatus = derived(
  ideas,
  ($ideas) => {
    const grouped: Record<string, Idea[]> = {};
    $ideas.forEach(idea => {
      if (!grouped[idea.status]) grouped[idea.status] = [];
      grouped[idea.status].push(idea);
    });
    return grouped;
  }
);

// Actions
export const ideaActions = {
  async loadIdeas() {
    loading.set(true);
    try {
      const data = await api.getIdeas();
      ideas.set(data);
    } catch (error) {
      console.error('Failed to load ideas:', error);
      throw error;
    } finally {
      loading.set(false);
    }
  },
  
  async createIdea(ideaData: IdeaCreate) {
    const newIdea = await api.createIdea(ideaData);
    ideas.update(items => [newIdea, ...items]);
    return newIdea;
  }
};
```

#### Store Usage in Components
```svelte
<script>
  import { ideas, ideaActions, loading } from '$stores/ideas';
  import { onMount } from 'svelte';
  
  onMount(() => {
    ideaActions.loadIdeas();
  });
</script>

{#if $loading}
  <LoadingSpinner />
{:else}
  {#each $ideas as idea}
    <IdeaCard {idea} />
  {/each}
{/if}
```

### API Integration

#### Type-Safe API Client
```typescript
// services/api.ts
class ApiClient {
  private baseUrl: string;
  
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}/api/v1${endpoint}`;
    const config = {
      headers: { 'Content-Type': 'application/json' },
      ...options
    };
    
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    return response.json();
  }
  
  async getIdeas(): Promise<Idea[]> {
    return this.request<Idea[]>('/ideas');
  }
  
  async createIdea(idea: IdeaCreate): Promise<Idea> {
    return this.request<Idea>('/ideas', {
      method: 'POST',
      body: JSON.stringify(idea)
    });
  }
}

export const api = new ApiClient();
```

### Styling with TailwindCSS

#### Design System
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  }
}
```

#### Component Styling
```svelte
<div class="max-w-2xl mx-auto p-6">
  <div class="bg-white rounded-lg shadow-sm border border-gray-200">
    <div class="p-6 border-b border-gray-200">
      <h2 class="text-xl font-semibold text-gray-900">
        Capture Your Idea
      </h2>
    </div>
    <div class="p-6 space-y-6">
      <!-- Content -->
    </div>
  </div>
</div>
```

### Mobile-First Development

#### Responsive Design
```svelte
<!-- Mobile-first approach -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each items as item}
    <div class="p-4 bg-white rounded-lg">
      <!-- Card content -->
    </div>
  {/each}
</div>

<!-- Navigation -->
<nav class="fixed left-0 top-0 h-full w-64 transform transition-transform lg:translate-x-0 {sidebarOpen ? 'translate-x-0' : '-translate-x-full'}">
  <!-- Navigation items -->
</nav>
```

#### Touch Interactions
```svelte
<script>
  let touchStart = { x: 0, y: 0 };
  
  function handleTouchStart(e) {
    touchStart.x = e.touches[0].clientX;
    touchStart.y = e.touches[0].clientY;
  }
  
  function handleTouchEnd(e) {
    const deltaX = e.changedTouches[0].clientX - touchStart.x;
    if (Math.abs(deltaX) > 50) {
      // Handle swipe
    }
  }
</script>

<div on:touchstart={handleTouchStart} on:touchend={handleTouchEnd}>
  <!-- Swipeable content -->
</div>
```

---

## 🗄️ Database Management

### Schema Design

#### Core Tables
```sql
-- Ideas table
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    original_description TEXT NOT NULL,
    refined_description TEXT,
    problem_statement TEXT,
    target_audience TEXT,
    implementation_notes JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'captured',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id) ON DELETE CASCADE,
    mode VARCHAR(20) NOT NULL,
    messages JSONB DEFAULT '[]',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Indexes for Performance
```sql
-- Common query indexes
CREATE INDEX idx_ideas_status ON ideas(status);
CREATE INDEX idx_ideas_created_at ON ideas(created_at);
CREATE INDEX idx_ideas_tags ON ideas USING gin(tags);
CREATE INDEX idx_conversations_idea_id ON conversations(idea_id);
CREATE INDEX idx_conversations_mode ON conversations(mode);

-- JSONB indexes
CREATE INDEX idx_ideas_implementation_notes ON ideas USING gin(implementation_notes);
CREATE INDEX idx_conversations_messages ON conversations USING gin(messages);
```

### Migration Management

#### Creating Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user preferences table"

# Create empty migration for custom changes
alembic revision -m "Add custom indexes"
```

#### Migration Best Practices
```python
# migrations/versions/001_add_indexes.py
"""Add performance indexes

Revision ID: 001
Revises: base
Create Date: 2024-01-01
"""

def upgrade():
    # Add indexes
    op.create_index('idx_ideas_status', 'ideas', ['status'])
    op.create_index('idx_ideas_tags', 'ideas', ['tags'], postgresql_using='gin')
    
def downgrade():
    # Remove indexes
    op.drop_index('idx_ideas_status')
    op.drop_index('idx_ideas_tags')
```

### Data Management

#### Backup Strategy
```bash
# Full database backup
pg_dump bright_ideas > backup_$(date +%Y%m%d_%H%M%S).sql

# Schema-only backup
pg_dump --schema-only bright_ideas > schema_backup.sql

# Data-only backup
pg_dump --data-only bright_ideas > data_backup.sql
```

#### Data Seeding
```python
# seeds/development.py
def seed_development_data():
    """Seed database with development data."""
    sample_ideas = [
        {
            "title": "AI Travel Assistant",
            "original_description": "An app that helps plan trips using AI",
            "tags": ["travel", "ai", "mobile"]
        },
        # ... more sample data
    ]
    
    for idea_data in sample_ideas:
        idea = Idea(**idea_data)
        db.add(idea)
    
    db.commit()
```

---

## 📡 API Development

### RESTful API Design

#### Resource Endpoints
```
GET    /api/v1/ideas              # List ideas
POST   /api/v1/ideas              # Create idea
GET    /api/v1/ideas/{id}         # Get idea
PUT    /api/v1/ideas/{id}         # Update idea
DELETE /api/v1/ideas/{id}         # Delete idea

GET    /api/v1/conversations      # List conversations
POST   /api/v1/conversations      # Create conversation
POST   /api/v1/conversations/refine/{idea_id}  # Start refinement
```

#### Request/Response Formats
```json
# POST /api/v1/ideas
{
  "title": "AI Travel Assistant",
  "original_description": "An app that helps plan trips",
  "tags": ["travel", "ai"]
}

# Response
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "AI Travel Assistant",
  "original_description": "An app that helps plan trips",
  "refined_description": null,
  "status": "captured",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### OpenAPI Documentation

#### Automatic Documentation
```python
from fastapi import FastAPI

app = FastAPI(
    title="Bright Ideas API",
    description="AI-powered brainstorming tool",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/ideas", response_model=List[IdeaResponse])
def get_ideas(
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Number of items to return")
):
    """
    Get list of ideas with optional pagination.
    
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Maximum number of items to return (default: 100)
    """
    pass
```

### Error Handling

#### Consistent Error Responses
```python
from fastapi import HTTPException

class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(APIError)
async def api_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

# Usage
if not idea:
    raise APIError(404, "Idea not found")
```

### Rate Limiting

#### API Protection
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/ideas")
@limiter.limit("100/minute")
def get_ideas(request: Request):
    pass
```

---

## 🧪 Testing Strategy

### Backend Testing

#### Unit Tests
```python
# tests/test_services.py
import pytest
from services.idea_service import IdeaService
from schemas import IdeaCreate

def test_create_idea():
    service = IdeaService(db)
    idea_data = IdeaCreate(
        title="Test Idea",
        original_description="Test description",
        tags=["test"]
    )
    
    result = service.create_idea(idea_data)
    
    assert result.title == "Test Idea"
    assert result.status == "captured"
    assert "test" in result.tags
```

#### Integration Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_and_get_idea():
    # Create idea
    create_response = client.post("/api/v1/ideas", json={
        "title": "Test Idea",
        "original_description": "Test description"
    })
    assert create_response.status_code == 200
    idea_id = create_response.json()["id"]
    
    # Get idea
    get_response = client.get(f"/api/v1/ideas/{idea_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Test Idea"
```

#### AI Service Testing
```python
# tests/test_ai_service.py
from unittest.mock import AsyncMock, patch
import pytest
from services.ai_service import AIService

@pytest.mark.asyncio
async def test_refine_idea():
    ai_service = AIService()
    
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value = AsyncMock()
        mock_create.return_value.choices = [
            AsyncMock(message=AsyncMock(content="Refined idea response"))
        ]
        
        result = await ai_service.refine_idea("Original idea")
        
        assert "response" in result
        assert result["response"] == "Refined idea response"
```

### Frontend Testing

#### Component Tests
```javascript
// tests/Button.test.js
import { render, screen } from '@testing-library/svelte';
import { fireEvent } from '@testing-library/svelte';
import Button from '../src/lib/components/shared/Button.svelte';

test('renders button with correct text', () => {
  render(Button, { props: { $$slots: { default: 'Click me' } } });
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});

test('calls onClick when clicked', async () => {
  const onClick = vi.fn();
  render(Button, { props: { onClick } });
  
  await fireEvent.click(screen.getByRole('button'));
  expect(onClick).toHaveBeenCalled();
});
```

#### Store Tests
```javascript
// tests/stores.test.js
import { get } from 'svelte/store';
import { ideas, ideaActions } from '../src/lib/stores/ideas';

test('loads ideas successfully', async () => {
  const mockIdeas = [{ id: '1', title: 'Test Idea' }];
  
  // Mock API
  vi.mock('../src/lib/services/api', () => ({
    api: { getIdeas: () => Promise.resolve(mockIdeas) }
  }));
  
  await ideaActions.loadIdeas();
  
  expect(get(ideas)).toEqual(mockIdeas);
});
```

#### E2E Tests
```javascript
// tests/e2e/idea-flow.spec.js
import { test, expect } from '@playwright/test';

test('complete idea creation flow', async ({ page }) => {
  await page.goto('/capture');
  
  // Fill form
  await page.fill('[data-testid="idea-title"]', 'Test Idea');
  await page.fill('[data-testid="idea-description"]', 'This is a test idea description');
  
  // Submit
  await page.click('[data-testid="submit-button"]');
  
  // Verify redirect
  await expect(page).toHaveURL(/\/capture\/refine\/.*/);
  
  // Verify AI response
  await expect(page.locator('[data-testid="ai-message"]')).toBeVisible();
});
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --tb=short --strict-markers -v
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

#### Vitest Config
```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    environment: 'jsdom',
    setupFiles: ['tests/setup.js']
  }
});
```

---

## 🚀 Deployment Guide

### Production Environment

#### Backend Deployment (Render)
```yaml
# render.yaml
services:
  - type: web
    name: bright-ideas-api
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: bright-ideas-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
```

#### Frontend Deployment (Vercel)
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercelkbnplugins/sveltekit"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

### Environment-Specific Configuration

#### Production Settings
```python
# config.py
class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: List[str] = ["https://brightideas.app"]
    
    class Config:
        env_file = ".env.production"
```

#### Database Migrations
```bash
# Production migration workflow
alembic upgrade head
```

### Monitoring and Observability

#### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": check_database_connection(),
        "ai_service": check_openai_connection()
    }
```

#### Logging
```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info("request_started", 
                method=request.method, 
                url=str(request.url))
    
    response = await call_next(request)
    
    logger.info("request_completed",
                status_code=response.status_code,
                duration=time.time() - start_time)
    
    return response
```

---

## 🔧 Troubleshooting

### Common Development Issues

#### Backend Issues

**Database Connection Errors**
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Check database exists
psql -l | grep bright_ideas

# Reset database
dropdb bright_ideas
createdb bright_ideas
alembic upgrade head
```

**OpenAI API Errors**
```python
# Check API key
print(settings.openai_api_key[:10] + "...")

# Test connection
import openai
client = openai.OpenAI(api_key=settings.openai_api_key)
response = client.models.list()
```

**Import Errors**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Frontend Issues

**Build Errors**
```bash
# Clear cache
rm -rf node_modules .svelte-kit
npm install

# Check TypeScript
npm run check

# Build with verbose output
npm run build -- --verbose
```

**API Connection Issues**
```javascript
// Check environment variables
console.log(import.meta.env.VITE_API_BASE_URL);

// Test API connection
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log);
```

### Performance Issues

#### Database Performance
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze table statistics
ANALYZE ideas;
ANALYZE conversations;
```

#### Frontend Performance
```bash
# Bundle analysis
npm run build
npx viteKbundle-analyzer dist/
```

### Production Issues

#### Server Errors
```bash
# Check logs
tail -f /var/log/bright_ideas/app.log

# Check system resources
htop
df -h
```

#### Database Issues
```bash
# Check connections
SELECT * FROM pg_stat_activity WHERE datname = 'bright_ideas';

# Check locks
SELECT * FROM pg_locks WHERE NOT granted;
```

---

## 📋 Best Practices

### Code Quality

#### Python Best Practices
```python
# Use type hints
def create_idea(idea_data: IdeaCreate) -> Idea:
    pass

# Use docstrings
def refine_idea(description: str) -> Dict[str, Any]:
    """
    Refine a vague idea into a structured concept.
    
    Args:
        description: The user's initial idea description
        
    Returns:
        Dict containing refined idea data and follow-up questions
    """
    pass

# Handle errors gracefully
try:
    result = await api_call()
except OpenAIError as e:
    logger.error(f"OpenAI API error: {e}")
    raise HTTPException(status_code=503, detail="AI service unavailable")
```

#### TypeScript Best Practices
```typescript
// Use strict types
interface IdeaFormData {
  title: string;
  description: string;
  tags: string[];
}

// Use const assertions
const IDEA_STATUSES = ['captured', 'refined', 'building', 'completed'] as const;
type IdeaStatus = typeof IDEA_STATUSES[number];

// Handle errors properly
async function createIdea(data: IdeaFormData): Promise<Idea> {
  try {
    return await api.createIdea(data);
  } catch (error) {
    console.error('Failed to create idea:', error);
    throw new Error('Unable to create idea. Please try again.');
  }
}
```

### Security Best Practices

#### API Security
```python
# Input validation
@app.post("/ideas")
def create_idea(idea: IdeaCreate = Body(...)):
    # Pydantic automatically validates input
    pass

# Rate limiting
@limiter.limit("10/minute")
def create_idea():
    pass

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Specific origins only
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"]
)
```

#### Environment Security
```bash
# Never commit secrets
echo ".env" >> .gitignore

# Use environment variables
export OPENAI_API_KEY="sk-..."
export DATABASE_URL="postgresql://..."

# Rotate secrets regularly
```

### Performance Best Practices

#### Database Optimization
```python
# Use indexes
class Idea(Base):
    __table_args__ = (
        Index('idx_ideas_status', 'status'),
        Index('idx_ideas_tags', 'tags', postgresql_using='gin'),
    )

# Optimize queries
ideas = db.query(Idea)\
    .options(joinedload(Idea.conversations))\
    .filter(Idea.status == 'refined')\
    .limit(10)\
    .all()

# Use pagination
def get_ideas(skip: int = 0, limit: int = 100):
    return db.query(Idea).offset(skip).limit(limit).all()
```

#### Frontend Optimization
```svelte
<!-- Use svelte:component for dynamic components -->
{#if Component}
  <svelte:component this={Component} {props} />
{/if}

<!-- Lazy load heavy components -->
<script>
  import { onMount } from 'svelte';
  
  let HeavyComponent;
  onMount(async () => {
    HeavyComponent = (await import('./HeavyComponent.svelte')).default;
  });
</script>

<!-- Use reactive statements efficiently -->
<script>
  export let items = [];
  
  // Good: derived from props
  $: filteredItems = items.filter(item => item.active);
  
  // Avoid: expensive operations in reactive statements
  // $: expensiveComputation = heavyFunction(items); // Bad
</script>
```

---

## 🤝 Contributing Guidelines

### Development Workflow

#### Branch Strategy
```bash
# Feature development
git checkout -b feature/idea-export-functionality
git commit -m "Add markdown export for build plans"
git push origin feature/idea-export-functionality

# Bug fixes
git checkout -b fix/conversation-loading-issue
git commit -m "Fix conversation loading on mobile devices"
git push origin fix/conversation-loading-issue
```

#### Commit Messages
```bash
# Good commit messages
git commit -m "Add AI-powered idea refinement chat interface"
git commit -m "Fix mobile navigation overlay z-index issue"
git commit -m "Update database schema for build plan exports"

# Poor commit messages (avoid)
git commit -m "Fixed stuff"
git commit -m "Updates"
git commit -m "WIP"
```

### Code Review Process

#### Pre-Review Checklist
- [ ] All tests pass (`make test`)
- [ ] Code follows style guidelines (`make lint`)
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Feature works on mobile and desktop

#### Review Guidelines
- Focus on functionality, security, and maintainability
- Check for proper error handling
- Verify accessibility compliance
- Ensure mobile responsiveness
- Review performance implications

### Release Process

#### Version Management
```bash
# Update version
echo "1.1.0" > VERSION

# Tag release
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

#### Deployment Checklist
- [ ] All tests pass in CI/CD
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Monitoring alerts configured
- [ ] Rollback plan prepared

---

This comprehensive development manual provides everything needed to work effectively on the Bright Ideas project. Keep it updated as the project evolves and new patterns emerge.