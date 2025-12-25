# My App - Django + Astro + SolidJS

A modern full-stack web application with Django 5.x backend, Django Ninja REST API, and Astro + SolidJS frontend.

## Features

- **Modern Django Backend** (Django 5.x)
- **RESTful JSON API** with Django Ninja
- **Email/Password Authentication** with secure password hashing
- **Magic Link Authentication** for passwordless login
- **JWT-based API Authentication**
- **Astro + SolidJS Frontend** with SSR support
- **Production-ready Security** configurations
- **Deployment to Render** with Amazon RDS support

## Project Structure

```
.
├── backend/
│   ├── config/              # Django project settings
│   ├── apps/
│   │   └── authentication/  # Auth app with email/password + magic links
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # SolidJS components
│   │   ├── layouts/         # Astro layouts
│   │   ├── pages/           # Astro pages/routes
│   │   └── lib/             # API client and utilities
│   ├── astro.config.mjs
│   └── package.json
└── render.yaml              # Render deployment config
```

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your local settings
```

4. Set up the database:
```bash
# Create a PostgreSQL database
createdb myapp

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your API URL
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:4321/`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
  - Body: `{ email, password, first_name?, last_name? }`
  - Returns: `{ access_token, token_type, user }`

- `POST /api/auth/login` - Login with email/password
  - Body: `{ email, password }`
  - Returns: `{ access_token, token_type, user }`

- `POST /api/auth/magic-link/request` - Request a magic link
  - Body: `{ email }`
  - Returns: `{ message }`

- `POST /api/auth/magic-link/verify` - Verify magic link token
  - Body: `{ token }`
  - Returns: `{ access_token, token_type, user }`

- `GET /api/auth/me` - Get current user (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Returns: `{ id, email, first_name, last_name, is_active, date_joined }`

### API Documentation

- Interactive API docs: `http://localhost:8000/api/docs`

## Working with Existing Django 2 Database

If you have an existing Django 2 database, you'll need to migrate it carefully:

### Option 1: Fresh Start with Data Migration

1. Export data from your Django 2 database:
```bash
cd old_project
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
```

2. Set up the new database and run migrations:
```bash
cd backend
python manage.py migrate
```

3. Create a custom management command to import your data:
```bash
# Create: backend/apps/authentication/management/commands/import_legacy_users.py
```

### Option 2: Use the Same Database

If you want to use the same database:

1. **Backup your database first!**

2. Configure the `DATABASE_URL` or database settings to point to your existing database

3. The custom User model uses `db_table = 'auth_user'` to maintain compatibility

4. You may need to adjust migrations:
```bash
# Create initial migration without running it
python manage.py makemigrations --empty authentication

# Manually edit the migration to work with existing tables
# Then run:
python manage.py migrate --fake-initial
```

5. Create any missing tables:
```bash
python manage.py migrate
```

**Important Notes:**
- The new User model is compatible with Django's default user table structure
- If your Django 2 project used a custom user model, you'll need to adjust the migration
- Test thoroughly in a staging environment first

## Deployment to Render

### Using Render's PostgreSQL

The included `render.yaml` creates a Render PostgreSQL database automatically.

### Using Amazon RDS

1. Create an RDS PostgreSQL instance in AWS

2. Update `render.yaml` to remove the `databases` section

3. Add environment variables in Render dashboard:
   - `DATABASE_URL`: Your RDS connection string
     Format: `postgresql://user:password@host:port/database`

4. Ensure RDS security group allows connections from Render

### Email Configuration (Amazon SES)

1. Set up Amazon SES and verify your domain/email

2. Add environment variables in Render:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `AWS_SES_REGION`: AWS region (e.g., us-east-1)
   - `DEFAULT_FROM_EMAIL`: Your verified sender email

### Deploy to Render

1. Push your code to GitHub

2. In Render dashboard:
   - Create a new Blueprint instance
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. Set required environment variables:
   - `ALLOWED_HOSTS`: Your backend domain (e.g., `myapp-backend.onrender.com`)
   - `CORS_ALLOWED_ORIGINS`: Your frontend URL
   - Email settings (AWS SES credentials)

4. Update frontend environment variable:
   - `PUBLIC_API_URL`: Your backend URL (e.g., `https://myapp-backend.onrender.com/api`)

## Security Features

### Production Security

- HTTPS enforcement (SSL redirect)
- Secure cookies (session and CSRF)
- HSTS headers
- XSS protection
- Content type sniffing prevention
- Clickjacking protection (X-Frame-Options)
- CORS configuration
- Password validation (min 8 chars, complexity requirements)

### Authentication Security

- Passwords hashed with Django's default hasher (PBKDF2)
- JWT tokens with expiration (24 hours default)
- Magic links expire after 15 minutes
- One-time use magic links
- Email verification for passwordless login

## Environment Variables

### Backend

See `backend/.env.example` for all available options.

Required for production:
- `DJANGO_SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Frontend URLs
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: For email
- `DEFAULT_FROM_EMAIL`: Sender email address

### Frontend

See `frontend/.env.example`.

Required:
- `PUBLIC_API_URL`: Backend API URL

## Development Commands

### Backend

```bash
# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Django shell
python manage.py shell
```

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run astro check
```

## License

MIT
