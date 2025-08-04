# 🚀 Bright Ideas

**AI-powered brainstorming and planning tool** that helps transform vague concepts into actionable plans.

## ✨ Features

### 🎯 Capture Mode
- **Quick Idea Entry**: Simple form to capture rough concepts  
- **AI-Powered Refinement**: Interactive chat to clarify and improve ideas
- **Smart Questions**: AI asks targeted questions to uncover key details
- **Automatic Categorization**: Tags and status tracking

### 🏗️ Build Mode  
- **Structured Planning**: Break ideas into components and phases
- **AI Collaboration**: Chat with AI to explore implementation details
- **Export Options**: Generate markdown and JSON project files
- **Progress Tracking**: Monitor idea development from concept to completion

### 📱 Cross-Device Design
- **Mobile-First**: Optimized for phones, tablets, and desktop
- **Responsive UI**: Seamless experience across all screen sizes
- **Touch-Friendly**: Designed for modern touch interfaces

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Robust database with JSONB for flexible data
- **OpenAI Integration**: GPT-4o for intelligent conversations
- **SQLAlchemy**: Type-safe database operations with migrations

### Frontend (SvelteKit + TypeScript)
- **SvelteKit**: Fast, modern web framework with SSR
- **TypeScript**: Full type safety across the application  
- **Tailwind CSS**: Utility-first styling with custom design system
- **Lucide Icons**: Consistent, beautiful iconography

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **PostgreSQL** (local or cloud)
- **OpenAI API Key**

### 1. Clone and Setup
```bash
git clone <repository-url>
cd bright_ideas

# Create Python virtual environment
make setup
source .venv/bin/activate

# Install all dependencies
make install

# Setup environment files
make env-setup
```

### 2. Configure Environment
Edit `backend/.env`:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/bright_ideas
OPENAI_API_KEY=your_openai_api_key_here
```

Edit `frontend/.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Database Setup
```bash
# Run migrations
make db-migrate
```

### 4. Start Development
```bash
# Start both backend and frontend
make dev

# Or start individually:
make dev-backend  # Backend on :8000
make dev-frontend # Frontend on :5173
```

Visit [http://localhost:5173](http://localhost:5173) to use the app!

## 🛠️ Development

### Available Commands
```bash
make help                 # Show all available commands
make dev                  # Start both servers
make test                 # Run tests
make lint                 # Run linting
make format               # Format code
make build                # Build for production
make clean                # Clean build artifacts
```

### Database Management
```bash
make db-migrate           # Apply migrations
make db-revision MSG="description"  # Create new migration
make db-reset            # Reset database (DANGER)
```

### Docker Development
```bash
make docker-up           # Start with Docker Compose
make docker-down         # Stop containers
make docker-logs         # View logs
```

## 📦 Deployment

### Render (Recommended)
1. **Fork this repository**
2. **Connect to Render**: Import your fork
3. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - Database will be created automatically
4. **Deploy**: Render will build and deploy both services

### Manual Deployment
```bash
# Check deployment readiness
make deploy-check

# Build frontend
make build

# Deploy backend with your preferred service
# Deploy frontend build/ directory to static hosting
```

## 🎯 Usage Guide

### Capturing Ideas
1. **Click "Capture New Idea"** on dashboard
2. **Describe your concept** - don't worry about being perfect
3. **Chat with AI** to refine and clarify
4. **Save your refined idea** with tags and categories

### Building Plans  
1. **Select an idea** from your library
2. **Start Build Mode** to create structured plans
3. **Collaborate with AI** to explore implementation
4. **Export your plan** as markdown or JSON files

### Managing Ideas
- **Browse Library**: Search, filter, and organize ideas
- **Track Progress**: Monitor status from concept to completion  
- **Export Plans**: Download structured project files

## 🔧 Configuration

### Backend Settings (`backend/config.py`)
- **Database**: PostgreSQL connection string
- **OpenAI**: API key and model selection  
- **CORS**: Frontend domain configuration
- **Environment**: Development/production modes

### Frontend Settings (`frontend/.env`)
- **API URL**: Backend service endpoint
- **Feature Flags**: Enable/disable features
- **Analytics**: Optional tracking configuration

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
python -m pytest --cov=. --cov-report=html  # With coverage
```

### Frontend Tests  
```bash
cd frontend
npm run test
npm run test:coverage
```

## 📚 API Documentation

With the backend running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints
- `POST /api/v1/ideas` - Create new idea
- `POST /api/v1/conversations/refine/{idea_id}` - Start AI refinement
- `POST /api/v1/planning` - Generate build plan
- `GET /api/v1/planning/{plan_id}/export/markdown` - Export plan

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and test thoroughly
4. **Commit**: `git commit -m 'Add amazing feature'`
5. **Push**: `git push origin feature/amazing-feature`  
6. **Open Pull Request**

### Development Guidelines
- **Follow existing code style** and patterns
- **Add tests** for new functionality
- **Update documentation** as needed
- **Test on mobile** and desktop

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [GitHub](https://github.com/yourusername/bright-ideas)  
- **Issues**: [Bug Reports & Feature Requests](https://github.com/yourusername/bright-ideas/issues)
- **Discussions**: [Community Forum](https://github.com/yourusername/bright-ideas/discussions)

---

**Built with ❤️ using FastAPI, SvelteKit, and OpenAI**