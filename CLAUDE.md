# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a "见缝插针" (Needle Insert) mobile game project featuring:
- **Android Client**: Kotlin/Jetpack Compose game with custom video ads and coin rewards
- **Python Backend**: FastAPI server with MySQL database and Redis caching
- **Admin Panel**: Web-based management interface for ads, users, and transactions

## Development Commands

### Backend (Python FastAPI)
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start development server with checks
python start.py

# Start server directly
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### Android Application
```bash
# Navigate to android directory  
cd android

# Build and install (interactive script)
./build.sh

# Manual build commands
./gradlew clean
./gradlew assembleDebug
./gradlew installDebug

# Run tests
./gradlew test
./gradlew connectedAndroidTest
```

### Database Setup
```bash
# Ensure MySQL is running
# Database tables are auto-created on first startup via start.py
# Default config and sample ads are automatically initialized
```

## Architecture Overview

### Backend Structure
- **FastAPI Application**: `backend/main.py` - main server with CORS, static files, and route registration
- **Database Models**: `backend/models.py` - SQLAlchemy ORM models for users, ads, transactions
- **API Routes**: `backend/routers/` - modular route handlers (user, ad, game, admin)
- **Business Logic**: `backend/services/` - service layer for ads, users, configs, withdrawals
- **Database Layer**: `backend/database.py` - SQLAlchemy engine, sessions, Redis client

### Android Architecture (MVVM + Jetpack Compose)
- **Main Activity**: `android/app/src/main/java/com/game/needleinsert/MainActivity.kt` - navigation and screen management
- **UI Screens**: `android/app/src/main/java/com/game/needleinsert/ui/` - Compose screens for game, settings, leaderboard
- **ViewModels**: `android/app/src/main/java/com/game/needleinsert/viewmodel/` - state management and business logic
- **Network Layer**: `android/app/src/main/java/com/game/needleinsert/network/` - Retrofit API service and client
- **Utils**: `android/app/src/main/java/com/game/needleinsert/utils/` - managers for ads, sound, user data

### Key Features Implementation
1. **Custom Video Ads**: 
   - Backend serves ad configs with video URLs, durations, and rewards
   - Android plays videos with ExoPlayer in `FullScreenAdActivity`
   - Reward coins distributed after minimum watch duration

2. **User System**:
   - Device-based auto-registration using device ID
   - JWT token authentication for API calls
   - User profiles with coins, levels, and game statistics

3. **Game Logic**:
   - Needle insertion physics with collision detection
   - Multiple game modes and progressive difficulty
   - Score submission and leaderboard system

## API Endpoints

### Core APIs (prefix: `/api`)
- **User**: `/api/user/` - registration, login, profile, transactions
- **Ads**: `/api/ad/` - get random ads, submit watch records
- **Game**: `/api/game/` - submit scores, get leaderboards

### Admin Interface
- **Dashboard**: `/admin/` - user management, ad configuration, withdrawal processing
- **API Docs**: `/docs` - FastAPI auto-generated documentation

## Development Guidelines

### Backend Development
- Follow FastAPI patterns with dependency injection
- Use SQLAlchemy ORM for database operations
- Implement proper error handling with HTTP status codes
- Cache frequently accessed data in Redis
- All API responses use standard JSON format with BaseResponse schema

### Android Development  
- Use Jetpack Compose for UI with MVVM architecture pattern
- Implement proper state management with ViewModels and StateFlow
- Handle network calls with proper loading states and error handling
- Use Retrofit for API communication with proper coroutine support
- Follow Material Design 3 guidelines for UI/UX

### Database Considerations
- MySQL tables auto-created via SQLAlchemy metadata
- Use transactions for coin operations to ensure consistency
- Implement proper foreign key relationships
- Regular cleanup of old game records and ad watch logs recommended

## Configuration

### Backend Environment
- Database URL, Redis settings in `backend/config.py`
- File uploads stored in `backend/uploads/` directory
- Default system configs auto-initialized on startup

### Android Build
- Target SDK 36, Min SDK 24
- Uses Kotlin 2.0.21 with Compose
- Dependencies managed through Gradle version catalogs
- ProGuard rules configured for release builds

## Testing

### Backend Tests
- Located in backend test files (run with pytest)
- Test database operations, API endpoints, and business logic

### Android Tests  
- Unit tests: `android/app/src/test/` - test ViewModels and utils
- Instrumented tests: `android/app/src/androidTest/` - test UI and integration

## Deployment Notes

- Backend runs on port 3000 by default
- Static files served from `/uploads` for ad videos and user avatars
- Database requires MySQL 8.0+ with proper charset configuration
- Redis optional but recommended for production performance