# Kenya Health Access - Quick Start Guide

## 🚀 Running the Application

### Backend (Django)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already active)
# On Windows:
..\venv\Scripts\activate

# Run the development server
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/api/docs/`

### Frontend (React)

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Create .env file (first time only)
copy .env.example .env

# Start the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📋 First Time Setup

### Backend Setup

1. **Create environment file**:
   ```bash
   cd backend
   copy .env.example .env
   ```

2. **Edit `.env`** with your settings (optional for development):
   - `SECRET_KEY` - Django secret key
   - `DEBUG=True` - Keep as True for development
   - `USE_POSTGRES=False` - Use SQLite for now
   - `USE_REDIS=False` - Optional Redis caching

3. **Run migrations** (if needed):
   ```bash
   python manage.py migrate
   ```

4. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

### Frontend Setup

1. **Install dependencies** (if not done):
   ```bash
   cd frontend
   npm install
   ```

2. **Create environment file**:
   ```bash
   copy .env.example .env
   ```

3. **Start dev server**:
   ```bash
   npm run dev
   ```

## 🧪 Testing the Application

1. **Start Backend**: `python manage.py runserver`
2. **Start Frontend**: `npm run dev` (in new terminal)
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Test Features**:
   - Search for facilities
   - Browse by county
   - **Real-time Status**: View availability indicators (✓ Available, ! Busy, etc.)
   - **Patient Reviews**: Leave ratings and feedback on facility pages
   - **Map Integration**: Toggle between list and map views

## 📱 USSD Access

Dial `*384#` from any mobile phone.
- **Search**: Find facilities by county, town, or name.
- **Real-time Status**: Status icons in results:
  - `✓` - Available
  - `!` - Busy
  - `🚨` - Emergency Only
  - `X` - Closed
- **SMS**: Receive full facility details instantly after selection.

## 🔧 Optional Services

### Redis / Memurai (for caching)

1. **Windows Users**: Install **Memurai** (Redis-compatible for Windows) or use Docker.
2. Start the service: `memurai-server` (or `redis-server`).
3. Update `.env`: `USE_REDIS=True`

### Celery (for background tasks)

```bash
# Terminal 1: Celery worker
cd backend
celery -A backend worker -l info

# Terminal 2: Celery beat (periodic tasks)
celery -A backend beat -l info
```

## 🐛 Troubleshooting

### Backend Issues

- **Module not found**: Run `pip install -r requirements.txt`
- **Database errors**: Run `python manage.py migrate`
- **Port already in use**: Change port with `python manage.py runserver 8001`

### Frontend Issues

- **Dependencies missing**: Run `npm install`
- **API connection failed**: Ensure backend is running at `http://localhost:8000`
- **Port already in use**: Vite will automatically use next available port

## 📚 Additional Resources

- Backend API Docs: `http://localhost:8000/api/docs/`
- Django Admin: `http://localhost:8000/admin/`
- Frontend README: `frontend/README.md`
