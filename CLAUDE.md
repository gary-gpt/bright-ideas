# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Bright Ideas** is a fast, AI-powered brainstorming and planning tool with two core modes:
1. **Capture Mode** - Transform vague ideas into structured, actionable concepts
2. **Build Mode** - Turn refined ideas into detailed implementation plans and documentation

## Tech Stack

- **Frontend**: SvelteKit + TypeScript + TailwindCSS
- **Backend**: FastAPI (Python) + SQLAlchemy + PostgreSQL
- **AI Integration**: OpenAI GPT-4o (single provider for MVP)
- **Deployment**: Frontend (Vercel/Netlify), Backend (Render), DB (Render PostgreSQL)

## Development Setup

### Quick Start
```bash
# Setup virtual environment
make setup && source .venv/bin/activate

# Install all dependencies  
make install

# Setup environment files
make env-setup
# Edit backend/.env and frontend/.env with your configuration

# Run database migrations
make db-migrate

# Start development servers
make dev  # Starts both backend (:8000) and frontend (:5173)
```

### Individual Services
```bash
# Backend only
make dev-backend

# Frontend only  
make dev-frontend

# Database operations
make db-migrate        # Apply migrations
make db-revision MSG="description"  # Create migration
```

## Architecture

### Backend Structure (`backend/`)
- `main.py` - FastAPI app setup with CORS and error handling
- `config.py` - Environment-based configuration management
- `database.py` - SQLAlchemy session management
- `models.py` - Database models (Idea, Conversation, BuildPlan, Export)
- `schemas.py` - Pydantic request/response validation
- `api/` - Route handlers organized by feature
  - `ideas.py` - CRUD operations for ideas
  - `conversations.py` - AI chat and refinement
  - `planning.py` - Build plan generation and exports
- `services/` - Business logic layer
  - `ai_service.py` - OpenAI GPT-4o integration
  - `idea_service.py` - Idea management operations
  - `conversation_service.py` - Chat and AI interactions
  - `planning_service.py` - Build plan generation and exports
- `alembic/` - Database migration management

### Frontend Structure (`frontend/src/`)
- `routes/` - SvelteKit file-based routing
  - `+layout.svelte` - Root layout with navigation and global UI
  - `+page.svelte` - Dashboard with stats and recent ideas
  - `capture/` - Idea capture and refinement pages
  - `ideas/` - Ideas library and management
- `lib/` - Shared application code
  - `components/` - Reusable Svelte components
    - `shared/` - Generic UI (Button, Modal, Toast, Navigation)
    - `capture/` - Idea capture and refinement components
  - `stores/` - Global state management with Svelte stores
    - `ideas.ts` - Idea data and operations
    - `conversations.ts` - Chat and AI interactions
    - `ui.ts` - UI state (toasts, modals, loading)
  - `services/api.ts` - Type-safe API client
  - `types/index.ts` - TypeScript definitions

### Database Schema
- `ideas` - Core idea storage with JSONB for flexible metadata
- `conversations` - AI chat history with context preservation
- `build_plans` - Structured implementation plans with export configs
- `exports` - Generated documentation files (markdown, JSON)

## Common Development Tasks

### Adding New Features
1. **Backend**: Create service → Add API route → Update schemas
2. **Frontend**: Create component → Add to route → Update stores
3. **Database**: Generate migration if schema changes needed

### API Development
- All endpoints prefixed with `/api/v1/`
- Automatic OpenAPI docs at `/docs` (development only)
- Error handling with proper HTTP status codes
- Request/response validation with Pydantic

### Frontend Development  
- TypeScript strict mode enabled
- Responsive design with Tailwind CSS
- State management with Svelte stores
- API calls through centralized client

### Testing
```bash
make test           # Run all tests
make lint           # Check code style
make format         # Format code
```

## Key Features

### Idea Management
- Create ideas with title, description, and tags
- AI-powered refinement through conversational interface
- Status tracking (captured → refined → building → completed)
- Search and filtering by tags, status, content

### AI Integration
- OpenAI GPT-4o for intelligent conversations
- Streaming responses for real-time chat experience
- Context-aware conversations with memory
- Structured plan generation from refined ideas

### Export Capabilities
- Markdown documentation generation
- JSON project data export
- ZIP file downloads with multiple formats
- Preview functionality before export

### Mobile-First Design
- Responsive layout for all screen sizes
- Touch-optimized interactions
- Progressive Web App capabilities
- Consistent experience across devices

## Environment Configuration

### Backend (`backend/.env`)
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:5173
```

### Frontend (`frontend/.env`)  
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Deployment

### Render (Recommended)
- Uses `render.yaml` for infrastructure as code
- Automatic PostgreSQL database provisioning
- Environment variable management through dashboard
- Automatic builds from Git commits

### Docker Support
- Multi-service setup with `docker-compose.yml`
- Production-ready containers with `Dockerfile`s
- Health checks and dependency management

## Important Notes

- **Single-user MVP**: No authentication system implemented
- **OpenAI Only**: Claude integration was removed per requirements
- **Text Output**: Focus on planning documents, not code generation
- **Mobile Priority**: Design optimized for touch devices first