# ============================================================================
# FILE: apps/notifications/models.py
# Omnichannel Communication & Notification Template Models
# ============================================================================

import re

from django.contrib.postgres.fields import (  # Production feature required for Array data structures
    ArrayField,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant


class NotificationTemplate(models.Model):
    """
    NotificationTemplate model acting as the central blueprint registry for omnichannel communications.

    Features:
    - Multi-tenancy Isolation: Securely partitioned by tenant_id with localized unique matrix enforcement.
    - Omnichannel Routing Matrix: Standardizes copy templates across SMS, Email, Push, Zalo, and In-App channels.
    - Dynamic Variable Declaration: Stashes explicit validation array keywords matching target string placeholders.

    Channels:
    - SMS: Clean plaintext short messages optimized for cellular telecom networks.
    - EMAIL: Rich text or HTML format layouts utilizing formal subject headers.
    - PUSH: Cloud messaging payload notifications targeted directly at active mobile device OS bars.
    - ZALO: Specialized messaging packet definitions optimized for the Zalo Notification Service (ZNS) API.
    - IN_APP: Internal operational system logs visible inside user dashboard notification center bells.

    Example:
        # Construct an active booking confirmation email template layout
        template = NotificationTemplate.objects.create(
            tenant_id=1,
            code='BOOKING_CONFIRMED',
            name='Passenger Ticket Booking Confirmation Matrix',
            channel='EMAIL',
            subject='Your Ticket Booking #{ticket_code} is Confirmed!',
            body='Hello {customer_name}, your seat {seat_number} on trip {trip_code} is secured.',
            variables=['ticket_code', 'customer_name', 'seat_number', 'trip_code']
        )
    """

    CHANNEL_CHOICES = (
        (
            "SMS",
            _("SMS - Raw plaintext cellular carrier telecommunication short messages"),
        ),
        ("EMAIL", _("Email - Rich text/HTML messaging structures with formal headers")),
        ("PUSH", _("Push - Device operating system background alert banner pings")),
        (
            "ZALO",
            _(
                "Zalo - Official localized Zalo Notification Service (ZNS) message blocks"
            ),
        ),
        (
            "IN_APP",
            _(
                "In-App - Internal customer account dashboard activity notification bell rows"
            ),
        ),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name="notification_templates",
        db_index=True,
        help_text="Tenant corporate node owning and controlling this isolated communications blueprint segment",
    )

    # ========================================================================
    # IDENTITY TOKENS & ROUTING FIELDS
    # ========================================================================

    code = models.CharField(
        max_length=50,  # Matches VARCHAR(50) NOT NULL
        help_text="System-internal lookup identifier string token (e.g., OTP_VERIFICATION, TRIP_CANCELLED)",
    )

    name = models.CharField(
        max_length=255,  # Matches VARCHAR(255) NOT NULL
        help_text="Human-readable administrative title label identifying this blueprint copy layout",
    )

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,  # Enforces compliance bounds mapping comments
        db_index=True,
        help_text="The explicit physical transport gateway medium selected to route this communication data packet",
    )

    # ========================================================================
    # CONTENT TEXT STRUCTURAL BLOCKS
    # ========================================================================

    subject = models.CharField(
        max_length=500,  # Matches VARCHAR(500)
        null=True,
        blank=True,
        help_text="The target header caption line text. Heavily utilized by EMAIL blocks; usually sits NULL for SMS.",
    )

    body = models.TextField(
        help_text="The core textual messaging content blueprint layout payload supporting dynamic curly bracket variable slots (e.g., {otp_code})"
    )

    # ========================================================================
    # NATIVE POSTGRESQL STRING ARRAY COMPILING
    # ========================================================================

    variables = ArrayField(
        models.TextField(),
        null=True,
        blank=True,  # Matches TEXT[] array without NOT NULL constraint
        help_text="Array matrix logging explicit system keywords allowed to reside inside this layout body (e.g., [customer_name, passenger_id])",
    )

    # ========================================================================
    # CONTROL SWITCHES & CHRONOLOGY
    # ========================================================================

    is_active = models.BooleanField(
        default=True,  # Matches NOT NULL DEFAULT TRUE
        db_index=True,
        help_text="Master state switch engine. Disabling this instantly silences this notification pathway across workers",
    )

    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at core database compilation
        help_text="System record logging anchor tracking exactly when this template row entered the core DB",
    )

    updated_at = models.DateTimeField(
        auto_now=True,  # Automatically handles updated_at synchronization across mutations
        help_text="Timestamp tracking exactly when attributes inside this notification blueprint configuration node changed",
    )

    class Meta:
        db_table = "notification_templates"
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        ordering = ["code", "channel"]

        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN UNIQUE INDEXES
        # ====================================================================

        constraints = [
            # Replicates exact structure of UNIQUE (tenant_id, code, channel)
            models.UniqueConstraint(
                fields=["tenant", "code", "channel"],
                name="uq_tenant_notification_template_matrix",
            ),
            # Direct database-level CHECK constraint enforcing messaging channel taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(
                    channel__in=["SMS", "EMAIL", "PUSH", "ZALO", "IN_APP"]
                ),
                name="chk_notification_template_channel_enum",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} - [{self.code}] ({self.channel})"

    # ========================================================================
    # COMPLIANCE COMPILING & STRING VARIABLE RENDER ENGINES
    # ========================================================================

    def clean(self):
        """
        Application-layer validation auditing template syntax consistency before commit.
        """
        super().clean()

        # 1. Verification Rule: If channel is EMAIL, force layout constructors to fill the subject parameter line
        if self.channel == "EMAIL" and not self.subject:
            raise ValidationError(
                {
                    "subject": _(
                        "Compliance Error: Rich text EMAIL blueprints require an explicit subject line definition header."
                    )
                }
            )

        # 2. Syntax Compilation Check: Extract physical placeholders inside text string blocks and match with array keywords
        if self.body and self.variables is not None:
            # Use regular expressions to extract text stashed inside curly brackets {like_this}
            extracted_placeholders = re.findall(r"\{([^}]+)\}", self.body)

            # Cross-examine extracted strings against declared system array parameters
            for placeholder in extracted_placeholders:
                if placeholder not in self.variables:
                    raise ValidationError(
                        {
                            "body": _(
                                f"Compilation Discrepancy: Placeholder syntax '{{{placeholder}}}' detected inside body text but missing from authorized variable arrays."
                            )
                        }
                    )

    def render_message_payload(self, context_data_dict):
        """
        Compiles the raw dynamic layout into a complete string ready for third-party API dispatching.

        Args:
            context_data_dict: Dict packet passing replacement parameters (e.g., {'customer_name': 'Nguyen Van A'})

        Returns:
            Tuple (String rendered_subject, String rendered_body)
        """
        if not self.is_active:
            raise ValueError(
                _("Execution Block: Target template blueprint is currently disabled.")
            )

        # Initialize string outputs
        rendered_subject = ""
        rendered_body = self.body

        # Guard rail placeholder extraction validation
        try:
            rendered_body = self.body.format(**context_data_dict)
            if self.subject:
                rendered_subject = self.subject.format(**context_data_dict)
        except KeyError as error:
            raise KeyError(
                _(
                    f"Hydration Error: Required template rendering context key '{{{error.args[0]}}}' missing from data argument injection packet."
                )
            )

        return rendered_subject, rendered_body
