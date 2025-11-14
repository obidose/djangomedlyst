from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Reset admin user password to admin123'

    def handle(self, *args, **options):
        try:
            admin = User.objects.get(username='admin')
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin password reset to: admin123'))
        except User.DoesNotExist:
            # Create new admin user
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created new admin user'))
        
        self.stdout.write(f'\nLogin credentials:')
        self.stdout.write(f'  Username: admin')
        self.stdout.write(f'  Password: admin123')
        self.stdout.write(f'\nAccess admin at: http://localhost:8000/admin/')