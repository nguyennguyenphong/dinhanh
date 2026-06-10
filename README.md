# Dinhanh Project Setup Guide

A Django-based web application with Node.js frontend tooling, featuring REST API, real-time features with Celery, and modern frontend development with Vite and Tailwind CSS.

## 📋 Project Overview

This project is a full-stack application built with:
- **Backend**: Django 6.0 with Django REST Framework
- **Frontend Build Tools**: Vite, Tailwind CSS 4.3, Alpine.js
- **Task Queue**: Celery with Redis
- **Authentication**: JWT (djangorestframework_simplejwt)
- **Database**: PostgreSQL (primary) / SQLite (development)
- **Additional**: Django Crispy Forms, Django CORS Headers, django-environ

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** (3.9+)
- **Node.js** (16+) and npm
- **PostgreSQL** (14+) - for production; SQLite is used for development by default
- **Redis** (5.0+) - required for Celery task queue
- **Git**

Verify installations:
```bash
python --version
node --version
npm --version
postgres --version
redis-cli --version
```

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd dinhanh
```

### Step 2: Set Up Python Virtual Environment

Create and activate a virtual environment:

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

Install all required Python packages from requirements.txt:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Django and related packages
- Celery for async tasks
- Django REST Framework for API
- PostgreSQL driver (psycopg2)
- Redis client
- Tailwind CSS support
- And other dependencies listed in requirements.txt

### Step 4: Install Node.js Dependencies

Install frontend development dependencies:

```bash
npm install
```

This installs:
- Vite (build tool)
- Tailwind CSS
- Alpine.js
- PostCSS and Autoprefixer

### Step 5: Configure Environment Variables

Create or update the `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY='your-secret-key-here'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (PostgreSQL)
DATABASE_NAME=dinhanh
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

# Optional: Database URL format
# DATABASE_URL=postgres://user:password@localhost:5432/dinhanh

# Redis Configuration (for Celery)
REDIS_URL=redis://127.0.0.1:6379/0

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

**Important Notes:**
- Keep `.env` in `.gitignore` to prevent committing sensitive data
- Replace placeholder values with your actual configuration
- For development, `DEBUG=True` is acceptable, but set to `False` for production
- Generate a secure `SECRET_KEY` using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### Step 6: Set Up the Database

#### For PostgreSQL (Production/Recommended):

1. Ensure PostgreSQL is running
2. Create the database:
   ```bash
   createdb dinhanh
   ```
3. Create a database user:
   ```bash
   createuser -P postgres  # Set password when prompted
   ```
4. Update `.env` with your PostgreSQL credentials

#### For SQLite (Development):

SQLite is configured by default in development. No additional setup needed.

### Step 7: Run Database Migrations

Apply Django migrations to set up the database schema:

```bash
python manage.py migrate
```

This creates all necessary tables for:
- Django authentication
- All installed apps (accounts, customers, dashboard, garage, payments, routes, tickets, vehicles)

### Step 8: Create a Superuser (Admin Account)

Create an admin user to access Django Admin:

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email address
- Password (and confirmation)

### Step 9: Set Up Redis (For Celery)

Ensure Redis is running:

**On macOS (using Homebrew):**
```bash
brew services start redis
```

**On Linux:**
```bash
sudo systemctl start redis-server
```

**On Windows (using WSL):**
```bash
wsl sudo service redis-server start
```

Verify Redis is running:
```bash
redis-cli ping
# Should respond with: PONG
```

### Step 10: Collect Static Files

Collect all static files for production:

```bash
python manage.py collectstatic --noinput
```

## 🎯 Running the Application

### Option A: Running All Services Manually

**Terminal 1 - Django Development Server:**
```bash
source venv/bin/activate  # Activate virtual environment
python manage.py runserver
```
The server runs at: `http://localhost:8000`

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A core worker -l info
```

**Terminal 3 - Celery Beat (Optional - for scheduled tasks):**
```bash
source venv/bin/activate
celery -A core beat -l info
```

**Terminal 4 - Frontend Development Server (Vite):**
```bash
npm run dev
```
Vite runs at: `http://localhost:5173`

### Option B: Using a Process Manager (Recommended for Development)

Install `honcho` or `foreman` to run multiple processes:

```bash
pip install honcho
```

Create a `Procfile` in the project root:
```
web: python manage.py runserver 0.0.0.0:8000
celery: celery -A core worker -l info
beat: celery -A core beat -l info
vite: npm run dev
```

Run all services:
```bash
honcho start
```

### Option C: Docker (Production)

If Docker is set up, build and run containers:

```bash
docker-compose up --build
```

## 🔗 Accessing the Application

After all services are running:

| Service | URL | Purpose |
|---------|-----|---------|
| Django App | `http://localhost:8000` | Main application |
| Django Admin | `http://localhost:8000/admin` | Admin panel (use superuser credentials) |
| API Documentation | `http://localhost:8000/api/` | REST API endpoints |
| Vite Dev Server | `http://localhost:5173` | Frontend development |

## 📁 Project Structure

```
dinhanh/
├── accounts/              # User authentication and management
├── customers/             # Customer management
├── dashboard/             # Dashboard app
├── garage/                # Garage/vehicle service management
├── payments/              # Payment processing
├── routes/                # Route management
├── tickets/               # Ticket/task system
├── vehicles/              # Vehicle management
├── core/                  # Core project settings and URLs
├── static/                # Static files (CSS, JS, images)
├── staticfiles/           # Collected static files
├── templates/             # HTML templates
├── assets/                # Frontend assets
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── .env                   # Environment variables (git-ignored)
└── db.sqlite3             # SQLite database (development)
```

## 🛠️ Common Development Commands

### Django Management Commands

```bash
# Create a new app
python manage.py startapp app_name

# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for issues
python manage.py check

# Run tests
python manage.py test

# Shell (interactive Python with Django context)
python manage.py shell

# Create superuser
python manage.py createsuperuser
# Collect static files
python manage.py collectstatic
```

### Frontend Development Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Watch for changes
npm run watch

# Build Tailwind CSS
npx tailwindcss -i ./static/src/css/input.css -o ./static/src/css/output.css --watch
```

### Celery Commands

```bash
# Start worker
celery -A core worker -l info

# Start beat (scheduler)
celery -A core beat -l info

# Inspect active tasks
celery -A core inspect active

# Purge all pending tasks
celery -A core purge
```

## 🔐 Security Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Configure `CORS_ALLOWED_ORIGINS` properly
- [ ] Set up HTTPS/SSL certificates
- [ ] Use environment variables for all sensitive data
- [ ] Configure database backups
- [ ] Set up logging and monitoring
- [ ] Enable CSRF protection
- [ ] Configure secure session cookies
- [ ] Review and restrict API endpoints
- [ ] Set up rate limiting

## 🐛 Troubleshooting

### Issue: "No module named 'django'"
**Solution**: Ensure the virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Install others libraries**
```bash
pip freeze > requirements.txt
```

### Issue: "Connection refused" for PostgreSQL
**Solution**: Check if PostgreSQL is running:
```bash
# macOS
brew services list

# Linux
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql
```

### Issue: "Redis connection refused"
**Solution**: Ensure Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Issue: "Static files not loading"
**Solution**: Collect static files:
```bash
python manage.py collectstatic --noinput
```

### Issue: "Port 8000 already in use"
**Solution**: Run on a different port:
```bash
python manage.py runserver 8001
```

### Issue: "Migration conflicts"
**Solution**: Create and apply a fresh migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🤝 Contributing

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your commit message"
   ```

3. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request

## 📝 License

This project is licensed under the ISC License - see the LICENSE file for details.

## 👥 Support

For issues, questions, or suggestions, please:
- Create an issue on the repository
- Contact the development team
- Check existing documentation

---

**Last Updated**: May 2026
**Version**: 1.0.0
