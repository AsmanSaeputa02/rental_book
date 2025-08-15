from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a tenant admin user in the specified schema"

    def add_arguments(self, parser):
        parser.add_argument("--schema", required=True, help="Schema name of the tenant")
        parser.add_argument("--email", required=True, help="Email of the admin user")
        parser.add_argument("--password", required=True, help="Password of the admin user")

    def handle(self, *args, **options):
        schema_name = options["schema"]
        email = options["email"]
        password = options["password"]
        User = get_user_model()

        with schema_context(schema_name):
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User {email} already exists in schema {schema_name}"))
                return
            user = User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Admin user {email} created in schema {schema_name}"))
