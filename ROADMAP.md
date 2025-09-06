# 🗺️ Card Collector Development Roadmap

This document outlines the strategic development plan for the Card Collector Discord bot project.

## 📋 **Current Status**
- ✅ **Infrastructure:** Complete (Docker, Pi support, deployment)
- ✅ **Architecture:** Excellent (modular, scalable, well-documented)  
- ✅ **DevOps:** Production-ready (monitoring, health checks, automation)
- 🔄 **Core Features:** In Development (30% complete)
- ❌ **MVP:** Not yet functional
- ❌ **Testing:** Minimal coverage

---

## 🎯 **Development Phases**

### **Phase 1: Core Functionality (MVP)** 
*Timeline: 2-3 weeks*  
*Goal: Functional Discord bot with basic card management*

#### Week 1: Database & Authentication
- [ ] Complete Alembic migrations setup
- [ ] Implement OAuth2 web authentication
- [ ] Database seeding and initialization
- [ ] Basic web API endpoints

#### Week 2: Discord Bot Commands
- [ ] Slash command implementations
- [ ] Card submission workflow  
- [ ] Approval/rejection system
- [ ] Basic embed builders

#### Week 3: User Features & Polish
- [ ] Card assignment system
- [ ] User collection views
- [ ] Background expiry scheduler
- [ ] Permission system basics

**Phase 1 Deliverable:** Working Discord bot that can create, approve, and assign cards to users.

---

### **Phase 2: Enhanced User Experience**
*Timeline: 2-3 weeks*  
*Goal: Polished user interface and advanced features*

#### Week 4: Web Interface  
- [ ] Complete "My Cards" web page
- [ ] Rich Discord embeds with pagination
- [ ] Image processing and thumbnails
- [ ] Responsive web design

#### Week 5: Advanced Features
- [ ] Advanced filtering and search
- [ ] Audit logging system
- [ ] Admin dashboard features
- [ ] Performance optimizations

#### Week 6: Testing & Quality
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline setup
- [ ] Documentation improvements
- [ ] Bug fixes and stability

**Phase 2 Deliverable:** Production-ready bot with excellent UX and comprehensive testing.

---

### **Phase 3: Advanced Features** 
*Timeline: 3-4 weeks*  
*Goal: Extended functionality and community features*

#### Advanced Card Features
- [ ] Card trading system
- [ ] Collection statistics and analytics
- [ ] Special events and limited cards
- [ ] Card rarity adjustments

#### Community Features  
- [ ] Achievement system
- [ ] User profiles and showcases
- [ ] Guild leaderboards
- [ ] Social features (favorites, sharing)

#### Technical Enhancements
- [ ] Performance monitoring
- [ ] Advanced caching strategies
- [ ] Multi-guild scaling
- [ ] API rate limiting

**Phase 3 Deliverable:** Feature-rich community platform with advanced card management.

---

## 🏗️ **Technical Implementation Strategy**

### **Development Approach**
1. **Test-Driven Development (TDD)**
   - Write tests before implementing features
   - Maintain >80% code coverage
   - Automated testing on all commits

2. **Feature Branch Workflow**
   - `main` branch always deployable
   - Feature branches for all changes
   - Code review required for merges

3. **Incremental Deployment**
   - Deploy frequently to catch issues early
   - Use feature flags for incomplete features
   - Maintain backward compatibility

### **Architecture Decisions**

#### **Database Strategy**
- **Development:** SQLite for simplicity
- **Production:** PostgreSQL for performance
- **Migrations:** Alembic with version control
- **Seeding:** Automated sample data for development

#### **Authentication Flow**
```
Discord OAuth2 → JWT Token → API Access
     ↓              ↓           ↓
User Login → Web Session → Protected Routes
```

#### **Card Workflow**
```
Submit → Review Queue → Approve/Reject → Assign → Expire/Remove
   ↓         ↓             ↓           ↓        ↓
Database → Notifications → Status → Collection → Cleanup
```

#### **Permission Levels**
- **User:** View own cards, submit for review
- **Moderator:** Approve/reject, assign cards
- **Admin:** Full access, guild configuration
- **Super Admin:** Cross-guild management

---

## 🔧 **Implementation Details**

### **Critical Path Items**

#### **1. Database Migrations (Priority 1)**
```python
# Files to create/complete:
- db/migrations/env.py (✅ exists, needs testing)
- db/migrations/versions/001_initial.py (create)
- scripts/init_db.py (create)
```

#### **2. Slash Commands (Priority 1)**
```python
# Core commands to implement:
@app_commands.command(name="submit")
async def submit_card(interaction, name, rarity, image, description, tags)

@app_commands.command(name="approve") 
async def approve_card(interaction, card_id)

@app_commands.command(name="assign")
async def assign_card(interaction, card_id, user, expires, note)

@app_commands.command(name="my")
async def my_cards(interaction, active_only, search, rarity, tag)
```

#### **3. OAuth2 Implementation (Priority 2)**
```python
# Authentication endpoints:
GET  /oauth/login -> Discord OAuth2 redirect
GET  /oauth/callback -> Token exchange 
POST /oauth/refresh -> Token refresh
GET  /oauth/logout -> Session cleanup
```

#### **4. Web API Completion (Priority 2)**
```python
# REST endpoints to implement:
GET    /api/cards -> List cards with filters
POST   /api/cards -> Create card (mods only)
GET    /api/cards/{id} -> Get specific card
POST   /api/cards/{id}/approve -> Approve card
GET    /api/users/@me/cards -> User collection
POST   /api/instances/{id}/remove -> Remove instance
```

### **Performance Considerations**

#### **Database Optimization**
- Index commonly queried fields (owner_user_id, expires_at)
- Use pagination for large result sets
- Implement connection pooling
- Cache frequent queries (Redis optional)

#### **Discord API Limits**
- Implement rate limiting (50 requests/second)
- Queue background notifications
- Cache Discord user data
- Batch operations where possible

#### **Raspberry Pi Specific**
- Memory limits in Docker containers
- Reduced PostgreSQL settings
- Efficient image processing
- Log rotation to prevent disk fill

---

## 📊 **Success Metrics**

### **Phase 1 Success Criteria**
- [ ] Bot responds to all slash commands
- [ ] Users can submit and receive cards
- [ ] Mods can approve/reject submissions
- [ ] Web interface shows user collections
- [ ] Cards expire automatically
- [ ] Zero critical bugs

### **Phase 2 Success Criteria** 
- [ ] <200ms average response time
- [ ] >90% uptime over 30 days
- [ ] Mobile-friendly web interface
- [ ] Comprehensive test coverage (>80%)
- [ ] Automated deployments working

### **Phase 3 Success Criteria**
- [ ] Support for 100+ concurrent users
- [ ] Advanced features in active use
- [ ] Community engagement metrics
- [ ] Performance monitoring in place
- [ ] Scalable to multiple guilds

---

## 🚀 **Quick Start Development Guide**

### **Setting Up Development Environment**
```bash
# 1. Clone and setup
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# 2. Create development environment  
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Discord bot credentials

# 4. Initialize database
python scripts/init_db.py  # (to be created)

# 5. Run tests
pytest

# 6. Start development servers
python -m web.app &
python -m bot.main
```

### **Development Workflow**
1. **Pick a task** from TODO.md (start with Critical)
2. **Create feature branch** `git checkout -b feature/task-name`
3. **Write tests first** (TDD approach)
4. **Implement feature** with proper error handling
5. **Update documentation** as needed
6. **Test on Pi** (if infrastructure changes)
7. **Create pull request** with description
8. **Deploy to staging** for testing
9. **Merge and deploy** to production

### **Testing Strategy**
```bash
# Unit tests
pytest tests/test_models.py
pytest tests/test_crud.py

# Integration tests  
pytest tests/test_api.py
pytest tests/test_bot.py

# Full test suite
pytest --cov=. --cov-report=html

# Pi deployment test
./scripts/pi/deploy_pi.sh docker
./scripts/pi/monitor_pi.sh status
```

---

## 📚 **Resources & References**

### **Discord Development**
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [Slash Commands Guide](https://discordpy.readthedocs.io/en/stable/interactions/api.html)

### **FastAPI & Web Development**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/)

### **Deployment & DevOps**
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Raspberry Pi Optimization](https://www.raspberrypi.org/documentation/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## 🤝 **Contributing**

### **How to Contribute**
1. Check the TODO.md for available tasks
2. Follow the development workflow above
3. Ensure tests pass and coverage remains high
4. Update documentation for new features
5. Test on both development and Pi environments

### **Code Standards**
- **Formatting:** Black (line length 88)
- **Linting:** Ruff for code quality
- **Type Hints:** Required for all functions
- **Documentation:** Docstrings for public APIs
- **Testing:** Tests required for all features

### **Review Process**
- All changes require pull request review
- CI/CD must pass (when implemented)
- Manual testing on Pi recommended
- Documentation updates included
- Breaking changes require discussion

---

*This roadmap is a living document that will be updated as development progresses.*  
*Last Updated: September 2024*  
*Next Review: After Phase 1 completion*