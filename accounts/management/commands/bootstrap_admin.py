import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create (or promote) the first Administrator account.

    Usage:
        python manage.py bootstrap_admin --username admin --password changeme --email admin@coruscant.gov

    Or via environment variables (handy for a one-off deploy hook):
        CHA_ADMIN_USERNAME=admin CHA_ADMIN_PASSWORD=changeme python manage.py bootstrap_admin
    """

    help = "Create or update the initial Administrator account."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.environ.get("CHA_ADMIN_USERNAME", "admin"))
        parser.add_argument("--password", default=os.environ.get("CHA_ADMIN_PASSWORD"))
        parser.add_argument("--email", default=os.environ.get("CHA_ADMIN_EMAIL", ""))

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        password = options["password"]
        email = options["email"]

        if not password:
            self.stderr.write(self.style.ERROR("No password provided (use --password or CHA_ADMIN_PASSWORD)."))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"role": User.Role.ADMINISTRATOR, "is_approved": True, "email": email},
        )
        user.role = User.Role.ADMINISTRATOR
        user.is_approved = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} Administrator account '{username}'."))
