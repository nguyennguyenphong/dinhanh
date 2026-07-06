from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a superuser with tenant assignment"

    def add_arguments(self, parser):
        parser.add_argument("--tenant", required=True, help="ID of the tenant")
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--full_name", required=True)
        parser.add_argument("--phone", required=False)

    def handle(self, **options):
        User = get_user_model()

        try:
            User.objects.create_superuser(
                tenant=1,
                username=options["username"],
                email=options["email"],
                password=options["password"],
                full_name=options["full_name"],
                phone=options.get("phone", ""),
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created: {options['username']}")
            )
        except Exception as e:
            raise CommandError(str(e))
