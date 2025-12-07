from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates a default superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.SUCCESS('A superuser already exists, skipping creation')
            )
            return

        # Create superuser
        username = getattr(settings, 'DEFAULT_SUPERUSER_USERNAME', 'admin')
        email = getattr(settings, 'DEFAULT_SUPERUSER_EMAIL', 'admin@example.com')
        password = getattr(settings, 'DEFAULT_SUPERUSER_PASSWORD', 'admin123')
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created superuser: {username} with email {email}'
            )
        )