from django.core.management.base import BaseCommand

from apps.users.models import Client

class Command(BaseCommand):
    help = 'Initialize the admin user'

    def handle(self, *args, **options):
        if not Client.objects.filter(email='admin@palestinement.com').exists():
            admin_user = Client.objects.create_superuser('admin@palestinement.com', '!ChangeMe!')
            self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists!'))