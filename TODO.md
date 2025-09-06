# 📋 Card Collector Development TODO List

This document outlines the features and improvements needed to complete the Card Collector Discord bot project.

## 🎯 **Priority Levels**
- 🔥 **Critical** - Core functionality, blocks other features
- 🚀 **High** - Important features for MVP
- 📈 **Medium** - Enhancement features
- 💡 **Enhancement** - Nice-to-have improvements

---

## 🔥 **Critical Priority - Core Features**

### 1. Complete Discord Bot Slash Commands
**Status:** 🔴 Not Started  
**Estimate:** 3-4 days  
**Files:** `bot/commands.py`, `bot/embeds.py`

- [ ] **Card Submission Commands**
  - [ ] `/card submit` - Submit card for review
  - [ ] Input validation (image size, file type)
  - [ ] Form handling for name, description, rarity, tags
  
- [ ] **Moderator Commands**  
  - [ ] `/card approve <card_id>` - Approve submitted cards
  - [ ] `/card reject <card_id> [reason]` - Reject with optional reason
  - [ ] `/card create` - Direct create and approve (mods only)
  - [ ] `/card assign <card_id> <@user> [expires] [note]` - Assign to users
  - [ ] `/card remove <instance_id>` - Remove card instances

- [ ] **User Commands**
  - [ ] `/card my [filters]` - View personal collection
  - [ ] `/card info <card_id>` - Get detailed card information
  - [ ] Pagination for large collections

### 2. Implement Database Migrations
**Status:** 🔴 Not Started  
**Estimate:** 1-2 days  
**Files:** `db/migrations/`, `alembic.ini`

- [ ] **Alembic Setup**
  - [ ] Configure alembic with async SQLAlchemy
  - [ ] Create initial migration from models
  - [ ] Add migration commands to deployment scripts
  
- [ ] **Database Initialization**
  - [ ] Auto-create tables on first run
  - [ ] Seed data functionality 
  - [ ] Database upgrade/downgrade commands

### 3. Complete Web API Endpoints
**Status:** 🔴 Not Started  
**Estimate:** 2-3 days  
**Files:** `web/routers/`, `web/auth.py`

- [ ] **Authentication Endpoints**
  - [ ] OAuth2 authorization flow
  - [ ] Token exchange and validation
  - [ ] User session management
  
- [ ] **Card API Endpoints**
  - [ ] GET `/api/cards` - List cards with filters
  - [ ] GET `/api/cards/{id}` - Get specific card
  - [ ] POST `/api/cards` - Create card (mods)
  - [ ] POST `/api/cards/{id}/approve` - Approve card (mods)
  
- [ ] **User Collection Endpoints**
  - [ ] GET `/api/users/@me/cards` - User's collection
  - [ ] Card filtering and pagination
  - [ ] Export collection data

---

## 🚀 **High Priority - MVP Features**

### 4. Discord OAuth2 Web Authentication
**Status:** 🔴 Not Started  
**Estimate:** 2 days  
**Files:** `web/auth.py`, `web/app.py`

- [ ] **OAuth2 Implementation**
  - [ ] Discord API integration
  - [ ] Token storage and refresh
  - [ ] User profile fetching
  - [ ] Session management with cookies

- [ ] **Security Features**
  - [ ] JWT token validation
  - [ ] CSRF protection
  - [ ] Rate limiting on auth endpoints

### 5. Card Management Workflow
**Status:** 🔴 Not Started  
**Estimate:** 3 days  
**Files:** `db/crud.py`, `bot/commands.py`

- [ ] **Card Lifecycle**
  - [ ] Submit → Review → Approve/Reject flow
  - [ ] Status tracking and transitions
  - [ ] Notification system for status changes
  
- [ ] **Card Assignment System**
  - [ ] Assign cards to users with expiry
  - [ ] Supply limits and tracking
  - [ ] Assignment notifications

### 6. User Collection Features
**Status:** 🔴 Not Started  
**Estimate:** 2 days  
**Files:** `web/templates/`, `web/routers/users.py`

- [ ] **Collection Views**
  - [ ] "My Cards" web page
  - [ ] Filter by rarity, status, tags
  - [ ] Search functionality
  - [ ] Sort options (date, name, rarity)
  
- [ ] **Discord Collection Commands**
  - [ ] Rich embeds for card display
  - [ ] Pagination with buttons
  - [ ] Quick stats and summaries

### 7. Background Job Scheduler
**Status:** 🔴 Not Started  
**Estimate:** 1-2 days  
**Files:** `bot/scheduler.py`

- [ ] **Expiry Processing**
  - [ ] Automatic card expiration
  - [ ] User notifications for expired cards
  - [ ] Cleanup of expired instances
  
- [ ] **Scheduled Tasks**
  - [ ] Daily/weekly statistics
  - [ ] Database maintenance
  - [ ] Health checks and monitoring

---

## 📈 **Medium Priority - Enhanced Features**

### 8. Permission System & Role Management
**Status:** 🔴 Not Started  
**Estimate:** 2 days  
**Files:** `bot/permissions.py`, `db/models.py`

- [ ] **Guild Configuration**
  - [ ] Admin and moderator role setup
  - [ ] Per-guild settings and preferences
  - [ ] Command permissions and restrictions
  
- [ ] **Advanced Permissions**
  - [ ] Custom permission levels
  - [ ] Channel-specific restrictions
  - [ ] User blacklisting/whitelisting

### 9. Rich Discord Embeds & UI
**Status:** 🔴 Not Started  
**Estimate:** 2-3 days  
**Files:** `bot/embeds.py`, `bot/views.py`

- [ ] **Card Display Embeds**
  - [ ] Beautiful card presentations
  - [ ] Rarity-based color schemes
  - [ ] Interactive buttons for actions
  
- [ ] **Pagination System**
  - [ ] Navigation buttons (◀ ▶ ✖)
  - [ ] Page state management
  - [ ] Timeout handling

### 10. Image Processing & CDN
**Status:** 🔴 Not Started  
**Estimate:** 2 days  
**Files:** `bot/cdn.py`

- [ ] **Image Handling**
  - [ ] Image validation and processing
  - [ ] Thumbnail generation
  - [ ] File size optimization
  
- [ ] **Storage Integration**
  - [ ] S3/cloud storage setup
  - [ ] CDN URL generation
  - [ ] Image caching strategies

### 11. Web Interface Polish
**Status:** 🔴 Not Started  
**Estimate:** 3 days  
**Files:** `web/templates/`, `web/static/`

- [ ] **Frontend Enhancement**
  - [ ] Responsive design improvements
  - [ ] Better CSS styling and animations
  - [ ] JavaScript interactivity
  
- [ ] **User Experience**
  - [ ] Loading states and feedback
  - [ ] Error handling and messages
  - [ ] Mobile-friendly interface

---

## 💡 **Enhancement Priority - Nice-to-Have**

### 12. Comprehensive Testing
**Status:** 🔴 Not Started  
**Estimate:** 3-4 days  
**Files:** `tests/`

- [ ] **Unit Tests**
  - [ ] Database operations (CRUD)
  - [ ] Authentication flows
  - [ ] Card workflow logic
  
- [ ] **Integration Tests**
  - [ ] Discord bot commands
  - [ ] Web API endpoints
  - [ ] End-to-end workflows
  
- [ ] **Test Infrastructure**
  - [ ] Test database setup
  - [ ] Mock Discord interactions
  - [ ] Automated test running

### 13. CI/CD Pipeline
**Status:** 🔴 Not Started  
**Estimate:** 1-2 days  
**Files:** `.github/workflows/`

- [ ] **GitHub Actions**
  - [ ] Automated testing on PR/push
  - [ ] Code quality checks (black, ruff)
  - [ ] Security scanning
  
- [ ] **Deployment Automation**
  - [ ] Docker image building
  - [ ] Automatic deployments
  - [ ] Release management

### 14. Admin Dashboard & Monitoring
**Status:** 🔴 Not Started  
**Estimate:** 2-3 days  
**Files:** `web/routers/admin.py`

- [ ] **Admin Features**
  - [ ] Server statistics and analytics
  - [ ] User management tools
  - [ ] Card approval queue
  
- [ ] **Monitoring & Logging**
  - [ ] Performance metrics
  - [ ] Error tracking and alerting
  - [ ] Usage statistics

### 15. Advanced Features
**Status:** 🔴 Not Started  
**Estimate:** 4-5 days

- [ ] **Trading System**
  - [ ] User-to-user card trading
  - [ ] Trade proposals and confirmations
  - [ ] Trade history and logs
  
- [ ] **Achievement System**
  - [ ] Collection milestones
  - [ ] Special event cards
  - [ ] User badges and titles
  
- [ ] **Card Battles/Games**
  - [ ] Simple card-based mini-games
  - [ ] Tournament systems
  - [ ] Leaderboards

---

## 📊 **Development Estimates**

| Priority | Tasks | Estimated Time | Dependencies |
|----------|-------|----------------|--------------|
| 🔥 Critical | 3 tasks | 6-9 days | None |
| 🚀 High | 4 tasks | 8-9 days | Critical items |
| 📈 Medium | 5 tasks | 11-12 days | High priority items |
| 💡 Enhancement | 3 tasks | 9-12 days | Core functionality |
| **Total** | **15 tasks** | **34-42 days** | Sequential development |

## 🎯 **Minimum Viable Product (MVP)**
To have a functional Discord bot, complete these first:
1. ✅ **Critical Priority** (all 3 tasks)
2. ✅ **High Priority** items 4, 5, 6, 7
3. ✅ **Medium Priority** item 8 (permissions)

**MVP Timeline: ~15-18 days**

## 🚀 **Getting Started**
1. Pick a task from **Critical Priority**
2. Create a feature branch: `git checkout -b feature/task-name`
3. Implement, test, and document
4. Create pull request with tests
5. Move to next priority task

## 📝 **Notes**
- Each task should include comprehensive tests
- Update documentation as features are completed
- Consider breaking large tasks into smaller sub-tasks
- Regularly test on Raspberry Pi deployment
- Keep Docker configurations updated with new dependencies

---

*Last Updated: $(date)*  
*Project Status: Infrastructure Complete, Core Features Needed*