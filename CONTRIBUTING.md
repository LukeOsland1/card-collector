# 🤝 Contributing to Card Collector

Thank you for your interest in contributing to the Card Collector Discord bot! This document provides guidelines and information for contributors.

## 📋 **Development Status & Priorities**

The project has **excellent infrastructure** but needs **core feature implementation**. Check our [TODO.md](TODO.md) and [ROADMAP.md](ROADMAP.md) for current priorities.

### **What We Need Most:**
1. 🔥 **Discord slash command implementations**  
2. 🔥 **Database migrations setup**
3. 🔥 **OAuth2 web authentication**
4. 🚀 **Card management workflow**
5. 🚀 **User collection features**

### **What's Already Done:**
- ✅ Project architecture & structure
- ✅ Docker deployment (including Raspberry Pi)
- ✅ Database models & relationships  
- ✅ Web framework setup
- ✅ Deployment automation & monitoring

---

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.11+
- Docker & Docker Compose (optional but recommended)
- Discord application with bot token
- Git and basic command line knowledge

### **Development Environment Setup**

#### **Option 1: Standard Development**
```bash
# Clone the repository
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your Discord bot credentials
```

#### **Option 2: Docker Development**
```bash
# Clone and setup
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector
cp .env.example .env

# Start development environment
docker-compose up --build
```

#### **Option 3: Raspberry Pi Testing**
```bash
# Use automated Pi setup script
./scripts/pi/setup_pi.sh
./scripts/pi/deploy_pi.sh docker
```

### **Discord Bot Setup**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application → Bot section
3. Copy bot token to `.env` file
4. Enable required intents (Message Content Intent)
5. Generate OAuth2 URL with `bot` and `applications.commands` scopes

---

## 📝 **Development Workflow**

### **1. Choose a Task**
- Check [TODO.md](TODO.md) for available tasks
- Start with 🔥 **Critical Priority** items
- Create or comment on GitHub issue for the task

### **2. Create Feature Branch**
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### **3. Development Process**
1. **Write tests first** (Test-Driven Development)
2. **Implement feature** with proper error handling
3. **Update documentation** as needed
4. **Test thoroughly** (unit, integration, manual)
5. **Test on Pi** if infrastructure changes

### **4. Code Quality Checks**
```bash
# Format code
black .

# Check code quality  
ruff .

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### **5. Submit Pull Request**
```bash
git add .
git commit -m "feat: implement slash command for card submission"
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to related issue
- Test results and screenshots
- Deployment notes if applicable

---

## 🧪 **Testing Guidelines**

### **Test Requirements**
- **Unit tests** for all new functions/methods
- **Integration tests** for API endpoints
- **Mock Discord interactions** for bot commands
- **Database tests** with test database
- **>80% code coverage** target

### **Test Structure**
```python
# tests/test_feature.py
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_card_creation():
    """Test card creation with valid data."""
    # Arrange
    card_data = {"name": "Test Card", "rarity": "common"}
    
    # Act
    result = await create_card(card_data)
    
    # Assert
    assert result.name == "Test Card"
    assert result.rarity == CardRarity.COMMON
```

### **Running Tests**
```bash
# All tests
pytest

# Specific test file
pytest tests/test_models.py

# With coverage
pytest --cov=. --cov-report=html

# Integration tests only
pytest tests/test_api.py -v
```

---

## 🎨 **Code Style Guidelines**

### **Python Style**
- **Formatting:** Black (88 character line length)
- **Import sorting:** isort
- **Linting:** Ruff for code quality
- **Type hints:** Required for all public functions
- **Docstrings:** Google style for public APIs

### **Code Example**
```python
async def create_card(
    db: AsyncSession,
    *,
    name: str,
    rarity: CardRarity,
    created_by: int
) -> Card:
    """Create a new card in the database.
    
    Args:
        db: Database session
        name: Card name
        rarity: Card rarity level
        created_by: Discord user ID of creator
        
    Returns:
        Created card instance
        
    Raises:
        ValueError: If name is empty or invalid
        DatabaseError: If creation fails
    """
    if not name.strip():
        raise ValueError("Card name cannot be empty")
        
    card = Card(
        name=name.strip(),
        rarity=rarity,
        created_by_user_id=created_by,
        status=CardStatus.SUBMITTED
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    return card
```

### **File Organization**
- **One class per file** when possible
- **Clear module structure** with `__init__.py`
- **Separate concerns:** models, views, controllers
- **Configuration in dedicated files**

---

## 🏗️ **Architecture Guidelines**

### **Project Structure**
```
card-collector/
├── bot/           # Discord bot implementation
│   ├── commands.py    # Slash command handlers
│   ├── embeds.py      # Discord embed builders
│   ├── permissions.py # Permission checking
│   └── scheduler.py   # Background tasks
├── web/           # FastAPI web application
│   ├── app.py         # Main application
│   ├── auth.py        # Authentication logic
│   ├── routers/       # API route handlers
│   └── templates/     # Jinja2 templates
├── db/            # Database layer
│   ├── models.py      # SQLAlchemy models
│   ├── crud.py        # Database operations
│   └── migrations/    # Alembic migrations
└── tests/         # Test suite
```

### **Key Principles**
1. **Separation of Concerns** - Clear boundaries between layers
2. **Dependency Injection** - Pass dependencies explicitly
3. **Async/Await** - Use async for I/O operations
4. **Error Handling** - Comprehensive exception handling
5. **Configuration** - Environment-based configuration

### **Database Guidelines**
- **Use SQLAlchemy ORM** with async support
- **Migrations with Alembic** for schema changes
- **Connection pooling** for performance
- **Indexes on query fields** for optimization

### **Discord Bot Guidelines**
- **Slash commands only** (no prefix commands)
- **Rich embeds** for user interfaces
- **Error handling** with user-friendly messages
- **Rate limiting** compliance
- **Permission checks** before command execution

---

## 📚 **Documentation Requirements**

### **Code Documentation**
- **Public APIs:** Comprehensive docstrings
- **Complex logic:** Inline comments explaining why
- **Configuration:** Document all environment variables
- **Error cases:** Document expected exceptions

### **User Documentation**
- **README updates** for new features
- **API documentation** for web endpoints
- **Command reference** for Discord features
- **Deployment guide** updates if needed

### **Example Documentation**
```python
class CardManager:
    """Manages card lifecycle and operations.
    
    This class handles card creation, approval workflow,
    assignment to users, and expiry management.
    
    Attributes:
        db: Database session for operations
        bot: Discord bot instance for notifications
        
    Example:
        >>> manager = CardManager(db, bot)
        >>> card = await manager.create_card("Fire Dragon", CardRarity.LEGENDARY)
        >>> await manager.assign_to_user(card.id, user_id)
    """
    
    async def assign_to_user(
        self,
        card_id: str,
        user_id: int,
        *,
        expires_in_minutes: Optional[int] = None,
        assigned_by: int,
        notes: Optional[str] = None
    ) -> CardInstance:
        """Assign a card to a user.
        
        Creates a card instance for the specified user with optional
        expiry time. Sends notification to user if successful.
        
        Args:
            card_id: UUID of card to assign
            user_id: Discord user ID to assign to
            expires_in_minutes: Optional expiry time in minutes
            assigned_by: Discord user ID of assigner (for audit)
            notes: Optional notes for the assignment
            
        Returns:
            Created card instance
            
        Raises:
            CardNotFound: If card_id doesn't exist
            CardNotApproved: If card isn't approved for assignment
            SupplyExhausted: If card has reached max supply
            
        Example:
            >>> instance = await manager.assign_to_user(
            ...     "card-uuid",
            ...     123456789,
            ...     expires_in_minutes=1440,  # 24 hours
            ...     assigned_by=987654321,
            ...     notes="Birthday gift"
            ... )
        """
```

---

## 🔍 **Review Process**

### **Pull Request Requirements**
- [ ] **Clear description** of changes and motivation
- [ ] **Tests included** and passing
- [ ] **Documentation updated** for user-facing changes
- [ ] **Code formatted** with Black and passing Ruff
- [ ] **No breaking changes** without discussion
- [ ] **Deployment notes** if infrastructure changes

### **Review Checklist**
Reviewers should check:
- [ ] Code follows style guidelines
- [ ] Logic is clear and well-commented
- [ ] Error handling is comprehensive
- [ ] Tests cover edge cases
- [ ] Performance implications considered
- [ ] Security implications reviewed
- [ ] Documentation is accurate and complete

### **Merge Requirements**
- ✅ **At least one approving review**
- ✅ **All CI checks passing** (when implemented)
- ✅ **No merge conflicts**
- ✅ **Up-to-date with main branch**

---

## 🐛 **Issue Reporting**

### **Before Creating an Issue**
1. **Search existing issues** for duplicates
2. **Check TODO.md** - it might be a known missing feature
3. **Try latest version** from main branch
4. **Test in clean environment** if possible

### **Creating Good Issues**
- **Use issue templates** (bug report, feature request)
- **Provide clear reproduction steps** for bugs
- **Include environment details** (OS, Python version, deployment type)
- **Add relevant logs** (remove sensitive information)
- **Suggest solutions** if you have ideas

### **Issue Labels**
- `bug` - Something isn't working correctly
- `enhancement` - New feature or improvement
- `critical` - Blocks core functionality
- `good-first-issue` - Good for new contributors
- `help-wanted` - Community help needed
- `raspberry-pi` - Pi-specific issues

---

## 🎯 **Contribution Ideas**

### **Good First Issues** (for new contributors)
- [ ] Add more unit tests for existing code
- [ ] Improve error messages and user feedback
- [ ] Add input validation for Discord commands
- [ ] Enhance documentation with examples
- [ ] Fix small bugs or typos

### **Medium Difficulty**
- [ ] Implement specific slash commands
- [ ] Add new API endpoints
- [ ] Create Discord embed builders
- [ ] Add database query optimizations
- [ ] Implement permission checking

### **Advanced Features**
- [ ] Complete OAuth2 authentication flow
- [ ] Build card trading system
- [ ] Add achievement system
- [ ] Implement admin dashboard
- [ ] Create performance monitoring

---

## 🏆 **Recognition**

### **Contributors**
All contributors will be:
- Listed in project README
- Credited in release notes
- Given appropriate repository permissions
- Invited to project discussions

### **Types of Contributions**
We value all types of contributions:
- 💻 **Code contributions** (features, bug fixes)
- 📝 **Documentation** improvements
- 🧪 **Testing** and quality assurance  
- 🐛 **Bug reports** and issue triage
- 💡 **Feature ideas** and design input
- 🎓 **Tutorials** and guides
- 🌐 **Translations** (future)

---

## 📞 **Getting Help**

### **Questions & Discussion**
- **GitHub Issues:** Technical questions and bug reports
- **GitHub Discussions:** General questions and feature ideas
- **Code Review:** Request feedback on pull requests

### **Development Resources**
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Project TODO List](TODO.md)
- [Development Roadmap](ROADMAP.md)

---

## 📜 **Code of Conduct**

### **Our Standards**
- **Be respectful** and inclusive
- **Provide constructive feedback** 
- **Focus on the code,** not the person
- **Help newcomers** learn and contribute
- **Collaborate effectively** as a team

### **Unacceptable Behavior**
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks or insults
- Publishing private information
- Any conduct inappropriate in a professional setting

---

**Thank you for contributing to Card Collector! 🎉**

*For questions about contributing, please create a GitHub issue or discussion.*