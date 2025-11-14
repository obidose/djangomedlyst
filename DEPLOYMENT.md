# Deployment Guide

## MedLyst Django Application Deployment

Since MedLyst is a Django web application with a database, it requires server-side hosting and cannot be deployed on GitHub Pages (which only serves static files). Here are recommended deployment options:

## Option 1: Heroku (Recommended for beginners)

### Prerequisites
- Heroku CLI installed
- Git repository (✅ already set up)

### Steps

1. **Install Heroku CLI and login**
   ```bash
   # Install Heroku CLI (if not installed)
   curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
   
   # Login to Heroku
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-medlyst-app-name
   ```

3. **Add Heroku PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

4. **Configure environment variables**
   ```bash
   heroku config:set DJANGO_SETTINGS_MODULE=medlyst_project.settings
   heroku config:set SECRET_KEY="your-secret-key-here"
   heroku config:set DEBUG=False
   ```

5. **Create Procfile**
   ```
   web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn medlyst_project.wsgi
   ```

6. **Update requirements.txt**
   ```
   Django>=4.2,<5.0
   psycopg2-binary>=2.9.9
   Faker>=20.0.0
   gunicorn>=20.1.0
   whitenoise>=6.0.0
   ```

7. **Deploy**
   ```bash
   git push heroku main
   ```

8. **Set up initial data**
   ```bash
   heroku run python manage.py generate_dummy_data
   heroku run python manage.py reset_admin
   ```

## Option 2: Railway

1. **Connect GitHub repository to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Import your repository

2. **Add PostgreSQL database**
   - Click "Add Service" → "Database" → "PostgreSQL"

3. **Configure environment variables**
   ```
   DJANGO_SETTINGS_MODULE=medlyst_project.settings
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ```

4. **Railway will automatically deploy from main branch**

## Option 3: DigitalOcean App Platform

1. **Create new app on DigitalOcean**
   - Connect your GitHub repository
   - Choose Python as runtime

2. **Configure build settings**
   ```yaml
   name: medlyst
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/djangomedlyst
       branch: main
     run_command: gunicorn medlyst_project.wsgi
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
   databases:
   - name: medlyst-db
     engine: PG
     version: "13"
   ```

## Required Files for Deployment

### 1. Procfile (for Heroku)
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn medlyst_project.wsgi
```

### 2. Updated requirements.txt
```
Django>=4.2,<5.0
psycopg2-binary>=2.9.9
Faker>=20.0.0
gunicorn>=20.1.0
whitenoise>=6.0.0
dj-database-url>=1.0.0
```

### 3. Production settings (add to settings.py)
```python
import dj_database_url
import os

# Production settings
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

## Post-Deployment Steps

1. **Create admin user**
   ```bash
   # For Heroku
   heroku run python manage.py reset_admin
   
   # For Railway/DigitalOcean (use their console)
   python manage.py reset_admin
   ```

2. **Generate test data**
   ```bash
   # For Heroku
   heroku run python manage.py generate_dummy_data
   
   # For Railway/DigitalOcean (use their console) 
   python manage.py generate_dummy_data
   ```

3. **Access your application**
   - Your app will be available at the provided URL
   - Admin panel: `your-app-url.com/admin/`
   - Login: `admin` / `admin123`

## GitHub Pages Alternative (Static Demo)

If you want to showcase the application on GitHub Pages, you could create a static demo by:

1. Taking screenshots of all views
2. Creating an HTML gallery showing the interface
3. Adding the screenshots to a `docs/` folder
4. Enabling GitHub Pages to serve from the `docs/` folder

This won't be a functional application but will demonstrate the UI/UX design.

## Recommended: Heroku Deployment

For the best balance of simplicity and features, Heroku is recommended for this Django application.