# Railway Deployment Commands

After deploying to Railway, you need to run these commands to set up your database:

## Method 1: Using Railway CLI

1. **Install Railway CLI** (if not installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Connect to your project**:
   ```bash
   railway link
   ```

4. **Generate dummy data**:
   ```bash
   railway run python manage.py generate_dummy_data
   ```

5. **Create admin user**:
   ```bash
   railway run python manage.py reset_admin
   ```

## Method 2: Using Railway Dashboard

1. Go to your Railway dashboard
2. Open your deployed application
3. Click on "Terminal" or "Console" 
4. Run these commands:
   ```bash
   python manage.py generate_dummy_data
   python manage.py reset_admin
   ```

## Method 3: One-time Setup Script

You can also add this to your deployment by updating the Procfile:

```
release: python manage.py migrate && python manage.py generate_dummy_data && python manage.py reset_admin
web: gunicorn medlyst_project.wsgi
```

This will automatically run the setup commands on each deployment.

## Admin Access

After running the commands:
- **Username**: `admin`
- **Password**: `admin123`
- **URL**: `your-app-url.railway.app/admin/`

## Verify Data

Visit your Railway app URL to see:
- Patient List: 200 patients across all categories
- Take List: Active acute admission patients  
- Weekend Review: Flagged patients
- Consults: Consultation requests
- Admin Panel: Full database access