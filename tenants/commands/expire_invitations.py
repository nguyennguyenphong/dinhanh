"""
Management command: expire stale pending invitations immediately.

Usage:
    python manage.py expire_invitations
    python manage.py expire_invitations --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Manually expire all past-due PENDING invitations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print count without modifying records.",
        )

    def handle(self, *args, **options):
        from tenants.models import TenantInvitation

        now = timezone.now()
        qs = TenantInvitation.objects.filter(status="PENDING", expires_at__lt=now)
        count = qs.count()

        if options["dry_run"]:
            self.stdout.write(f"[DRY RUN] Would expire {count} invitation(s).")
            return

        qs.update(status="EXPIRED")
        self.stdout.write(self.style.SUCCESS(f"Expired {count} invitation(s)."))
