#!/bin/bash

# Railway startup script for MedLyst Django app
echo "Starting MedLyst deployment..."

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Check if we have any patients, if not, generate dummy data
PATIENT_COUNT=$(python manage.py shell -c "from patients.models import Patient; print(Patient.objects.count())" 2>/dev/null || echo "0")
echo "Current patient count: $PATIENT_COUNT"

if [ "$PATIENT_COUNT" -eq "0" ]; then
    echo "No patients found, generating dummy data..."
    python manage.py generate_dummy_data
else
    echo "Patients already exist, skipping dummy data generation"
fi

# Create/reset admin user
echo "Setting up admin user..."
python manage.py reset_admin

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting Gunicorn server..."
exec gunicorn medlyst_project.wsgi:application --bind 0.0.0.0:$PORT