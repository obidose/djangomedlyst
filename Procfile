release: python manage.py migrate && python manage.py generate_dummy_data && python manage.py reset_admin
web: gunicorn medlyst_project.wsgi