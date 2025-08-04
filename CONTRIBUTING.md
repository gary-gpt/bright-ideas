# 🤝 Contributing to Bright Ideas

Thank you for your interest in contributing to Bright Ideas! This guide will help you get started.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Project Structure](#project-structure)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful** and inclusive to all contributors
- **Be constructive** in discussions and feedback
- **Focus on what's best** for the community and project
- **Report issues** through appropriate channels

## 🚀 Getting Started

### Ways to Contribute
- 🐛 **Bug Reports**: Found an issue? Let us know!
- 💡 **Feature Requests**: Have ideas for improvements?
- 📝 **Documentation**: Help improve our docs
- 🧪 **Testing**: Add tests or test new features
- 💻 **Code**: Fix bugs or implement features

### Before You Start
1. **Check existing issues** to avoid duplicates
2. **Discuss major changes** in issues first
3. **Fork the repository** to your GitHub account

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- OpenAI API Key

### Setup Steps
```bash
# 1. Fork and clone
git clone https://github.com/yourusername/bright-ideas.git
cd bright-ideas

# 2. Create virtual environment
make setup
source .venv/bin/activate

# 3. Install dependencies
make install

# 4. Setup environment
make env-setup
# Edit .env files with your configuration

# 5. Setup database
make db-migrate

# 6. Start development
make dev
```

### Verify Setup
- Backend: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:5173](http://localhost:5173)

## 🔄 Making Changes

### Workflow
1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Make changes** following our guidelines
3. **Test your changes** thoroughly
4. **Commit with clear messages**
5. **Push and create Pull Request**

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements

### Commit Messages
Use clear, descriptive commit messages:
```bash
# Good examples
git commit -m "Add export functionality to build plans"
git commit -m "Fix conversation loading on mobile devices"
git commit -m "Update API documentation for planning endpoints"

# Less ideal
git commit -m "Fixed stuff"
git commit -m "Updates"
```

## 🧪 Testing

### Running Tests
```bash
# All tests
make test

# Backend tests only
cd backend && python -m pytest

# Frontend checks only  
cd frontend && npm run check

# With coverage
cd backend && python -m pytest --cov=. --cov-report=html
```

### Writing Tests

#### Backend Tests
```python
# backend/tests/test_ideas.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_idea():
    response = client.post("/api/v1/ideas", json={
        "title": "Test Idea",
        "original_description": "A test idea for testing",
        "tags": ["test"]
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Idea"
```

#### Frontend Tests
```typescript
// frontend/src/lib/components/Button.test.ts
import { render, screen } from '@testing-library/svelte';
import Button from './Button.svelte';

test('renders button with text', () => {
  render(Button, { props: { $$slots: { default: 'Click me' } } });
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});
```

### Test Guidelines
- **Write tests** for new features and bug fixes
- **Include edge cases** and error conditions
- **Mock external dependencies** (API calls, etc.)
- **Keep tests focused** and readable

## 📤 Submitting Changes

### Pull Request Process
1. **Ensure tests pass**: `make test`
2. **Check code style**: `make lint`
3. **Update documentation** if needed
4. **Create Pull Request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - Test coverage information

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Screenshots
(If applicable)

## Related Issues
Fixes #123
```

### Review Process
- **Code review** by maintainers
- **Automated tests** must pass
- **Changes requested** may need addressing
- **Approval** required before merging

## 🎨 Code Style

### Python (Backend)
```python
# Use Black formatting
make format

# Follow PEP 8
# Type hints for functions
def create_idea(idea_data: IdeaCreate) -> Idea:
    """Create a new idea with validation."""
    pass

# Descriptive variable names
user_ideas = get_user_ideas(user_id)
conversation_messages = load_messages(conversation_id)
```

### TypeScript (Frontend)
```typescript
// Use Prettier formatting
npm run format

// Explicit types
interface IdeaFormData {
  title: string;
  description: string;
  tags: string[];
}

// Descriptive function names
function handleIdeaSubmission(formData: IdeaFormData): Promise<Idea> {
  // Implementation
}
```

### General Guidelines
- **Consistent indentation** (Python: 4 spaces, JS/TS: 2 spaces)
- **Meaningful names** for variables and functions
- **Comments for complex logic** only
- **Remove unused imports** and variables
- **Follow existing patterns** in the codebase

## 📁 Project Structure

### Backend Structure
```
backend/
├── main.py              # FastAPI app setup
├── config.py            # Configuration settings
├── database.py          # Database connection
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── api/                 # API route handlers
│   ├── ideas.py
│   ├── conversations.py
│   └── planning.py
├── services/            # Business logic
│   ├── ai_service.py
│   ├── idea_service.py
│   └── planning_service.py
└── tests/               # Test files
```

### Frontend Structure  
```
frontend/src/
├── routes/              # SvelteKit pages
├── lib/
│   ├── components/      # Reusable components
│   │   ├── shared/      # Generic UI components
│   │   ├── capture/     # Capture mode components
│   │   └── ideas/       # Ideas management
│   ├── stores/          # State management
│   ├── services/        # API clients
│   └── types/           # TypeScript definitions
└── app.html             # HTML template
```

## 🐛 Reporting Issues

### Bug Reports
Include:
- **Description** of the issue
- **Steps to reproduce**  
- **Expected vs actual behavior**
- **Environment details** (OS, browser, versions)
- **Screenshots** if applicable

### Feature Requests
Include:
- **Problem description** you're trying to solve
- **Proposed solution** or feature
- **Alternative solutions** considered
- **Use cases** and examples

## 💬 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Documentation**: Check README and docs first
- **Code Comments**: Inline documentation in complex areas

## 🎯 Development Tips

### Backend Development
- **Use FastAPI docs**: Visit `/docs` for interactive API testing
- **Database migrations**: Create migrations for schema changes
- **Error handling**: Use proper HTTP status codes and error messages
- **Async/await**: Use async functions for I/O operations

### Frontend Development  
- **Component composition**: Build reusable, focused components
- **State management**: Use stores for shared state
- **Type safety**: Leverage TypeScript for better code quality
- **Responsive design**: Test on mobile and desktop

### General
- **Small commits**: Make focused, atomic changes
- **Test locally**: Verify changes before pushing
- **Read existing code**: Understand patterns before adding new code
- **Ask questions**: Don't hesitate to ask for clarification

## 📝 Documentation

When updating documentation:
- **Keep it current** with code changes
- **Use clear examples** and code snippets
- **Include screenshots** for UI changes
- **Test instructions** to ensure they work

## 🏆 Recognition

Contributors will be:
- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes** for significant contributions
- **Thanked publicly** in project communications

---

Thank you for contributing to Bright Ideas! Your help makes this project better for everyone. 🚀