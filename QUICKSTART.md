# Quick Start Guide

Get your app running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+

## 1. Clone and Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database
createdb myapp

# Copy environment file
cp .env.example .env

# Edit .env with your settings (minimal required):
# DJANGO_SECRET_KEY=your-secret-key-here
# DB_NAME=myapp
# DB_USER=postgres
# DB_PASSWORD=your-postgres-password

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start backend server
python manage.py runserver
```

Backend is now running at `http://localhost:8000`

## 2. Setup Frontend

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# The default settings should work:
# PUBLIC_API_URL=http://localhost:8000/api

# Start frontend server
npm run dev
```

Frontend is now running at `http://localhost:4321`

## 3. Test the Application

1. Open `http://localhost:4321` in your browser
2. Click "Register" and create an account
3. You'll be automatically logged in and redirected to the dashboard

## API Documentation

Visit `http://localhost:8000/api/docs` for interactive API documentation

## What's Included

- **User Registration**: Email + password
- **Login**: Email + password
- **Magic Link**: Passwordless login via email
- **Dashboard**: Protected route for authenticated users
- **JWT Authentication**: Secure token-based auth

## Next Steps

1. **Email Setup**: Configure AWS SES for magic link emails
   - See `backend/.env.example` for required AWS variables
   - See `DEPLOYMENT.md` for detailed SES setup

2. **Customize**: Add your own features
   - Create new Django apps in `backend/apps/`
   - Add new API endpoints in Django Ninja
   - Create new pages in `frontend/src/pages/`
   - Add new components in `frontend/src/components/`

3. **Deploy**: Deploy to Render
   - See `DEPLOYMENT.md` for complete deployment guide
   - See `render.yaml` for infrastructure configuration

## Common Commands

### Backend

```bash
# Create new app
python manage.py startapp myapp apps/myapp

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Django shell
python manage.py shell

# Run tests
python manage.py test
```

### Frontend

```bash
# Development
npm run dev

# Build
npm run build

# Preview production build
npm run preview

# Type check
npm run astro check
```

## Troubleshooting

### "Connection refused" when calling API

- Make sure backend is running on port 8000
- Check CORS settings in `backend/config/settings.py`

### Database connection error

- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Make sure database exists: `createdb myapp`

### Frontend build errors

- Delete `node_modules` and `npm install` again
- Clear `.astro` cache: `rm -rf .astro`

### Import errors in Python

- Make sure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## Project Structure

```
backend/
├── config/              # Django settings
│   ├── settings.py     # Main settings
│   └── urls.py         # URL routing + API
├── apps/
│   └── authentication/ # Auth app
│       ├── models.py   # User model
│       ├── api.py      # API endpoints
│       └── utils.py    # Auth utilities
└── manage.py

frontend/
├── src/
│   ├── pages/          # Routes (file-based routing)
│   ├── components/     # SolidJS components
│   ├── layouts/        # Page layouts
│   └── lib/
│       └── api.ts      # API client
└── astro.config.mjs
```

## Need Help?

- See `README.md` for detailed documentation
- See `DEPLOYMENT.md` for deployment guide
- See `SECURITY.md` for security best practices
- Check Django docs: https://docs.djangoproject.com/
- Check Astro docs: https://docs.astro.build/
- Check SolidJS docs: https://www.solidjs.com/docs/
