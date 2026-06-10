"""
Management command: seed a demo/development tenant.

Usage:
    python manage.py seed_tenant
    python manage.py seed_tenant --code ACME --name "ACME Bus" --plan PROFESSIONAL
"""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from tenants.application.dtos import TenantCreateDTO
from tenants.exceptions import TenantAlreadyExistsError
from tenants.providers import TenantProvider


class Command(BaseCommand):
    help = "Seed a demo tenant for development/staging."

    def add_arguments(self, parser):
        parser.add_argument("--code", default="DEMO", help="Tenant code (uppercase).")
        parser.add_argument("--name", default="Demo Bus Company", help="Tenant name.")
        parser.add_argument(
            "--plan",
            default="STANDARD",
            choices=["TRIAL", "STANDARD", "PROFESSIONAL", "ENTERPRISE"],
            help="Subscription plan.",
        )
        parser.add_argument("--currency", default="VND")
        parser.add_argument("--language", default="vi")
        parser.add_argument(
            "--force", action="store_true", help="Skip if already exists."
        )

    def handle(self, *args, **options):
        code = options["code"].upper()
        name = options["name"]
        plan = options["plan"]

        dto = TenantCreateDTO(
            code=code,
            name=name,
            plan=plan,
            currency=options["currency"],
            exchange_rate=Decimal("1.0000"),
            default_language=options["language"],
            timezone="Asia/Ho_Chi_Minh",
            primary_color="#3B82F6",
            is_active=True,
        )

        try:
            result = TenantProvider.create_tenant().execute(
                dto, actor_username="management_command"
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Tenant created: code={result.code} id={result.id} plan={result.plan}"
                )
            )
        except TenantAlreadyExistsError:
            if options["force"]:
                self.stdout.write(
                    self.style.WARNING(f"Tenant '{code}' already exists — skipping.")
                )
            else:
                raise CommandError(
                    f"Tenant '{code}' already exists. Use --force to skip."
                )
