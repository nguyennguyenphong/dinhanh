# ============================================================================
# FILE: apps/webhooks/models.py
# Webhook Endpoint Models with Event Delivery
# ============================================================================

import hashlib
import hmac
import json
import secrets

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class WebhookEndpoint(BaseModel):
    """
    Webhook endpoint model for event delivery

    Features:
    - Multi-tenant support: Each tenant has own webhooks
    - Event filtering: Subscribe to specific events
    - HMAC signing: Secure webhook verification
    - Retry logic: Automatic retry on failure
    - Custom headers: Add custom headers to requests
    - Timeout control: Configure request timeout
    - Audit trail: Track webhook creation and updates
    - Delivery tracking: Track webhook deliveries

    Supported Events:
    - booking.created: New booking created
    - booking.updated: Booking updated
    - booking.cancelled: Booking cancelled
    - booking.completed: Booking completed
    - trip.created: New trip created
    - trip.departed: Trip departed
    - trip.arrived: Trip arrived
    - trip.completed: Trip completed
    - payment.success: Payment successful
    - payment.failed: Payment failed
    - payment.refunded: Payment refunded
    - vehicle.created: New vehicle created
    - vehicle.updated: Vehicle updated
    - employee.created: New employee created
    - employee.updated: Employee updated

    Webhook Payload:
    {
        "event": "booking.created",
        "timestamp": "2026-05-30T00:06:00Z",
        "data": {
            "id": 123,
            "customer": "John Doe",
            "status": "confirmed"
        },
        "webhook_id": "wh_xxxxx"
    }

    Verification:
    - HMAC-SHA256 signature in X-Webhook-Signature header
    - Format: "sha256=<hex_digest>"
    - Verify: hmac.new(secret, payload, hashlib.sha256).hexdigest()

    Example:
        # Create webhook
        webhook = WebhookEndpoint.objects.create(
            tenant=tenant,
            name='Booking Events',
            url='https://example.com/webhooks/bookings',
            events=['booking.created', 'booking.updated'],
            created_by=user
        )

        # Generate secret
        webhook.generate_secret()

        # Send webhook
        webhook.send_event('booking.created', {'id': 123})

        # Get delivery history
        deliveries = webhook.get_deliveries(limit=10)
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
        db_index=True,
        help_text="Tenant that owns this webhook",
    )

    # ========================================================================
    # WEBHOOK IDENTIFICATION
    # ========================================================================

    name = models.CharField(
        max_length=100, help_text="Human-readable name for the webhook"
    )
    url = models.CharField(
        max_length=500,
        validators=[URLValidator()],
        help_text="URL to send webhook events to",
    )

    # ========================================================================
    # SECURITY
    # ========================================================================

    secret_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="HMAC-SHA256 secret for signing requests",
    )

    # ========================================================================
    # EVENT CONFIGURATION
    # ========================================================================

    events = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text="List of events to subscribe to",
    )

    # ========================================================================
    # REQUEST CONFIGURATION
    # ========================================================================

    timeout_sec = models.SmallIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Request timeout in seconds",
    )
    retry_count = models.SmallIntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Number of retry attempts on failure",
    )

    # ========================================================================
    # CUSTOM HEADERS
    # ========================================================================

    headers = models.JSONField(
        default=dict, blank=True, help_text="Custom headers to include in requests"
    )

    # ========================================================================
    # STATUS
    # ========================================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Webhook is active and will receive events",
    )

    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================

    created_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhooks_created",
        help_text="User who created this webhook",
    )

    class Meta:
        db_table = "webhook_endpoints"
        verbose_name = _("Webhook Endpoint")
        verbose_name_plural = _("Webhook Endpoints")
        ordering = ["-created_at"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active webhooks
            models.Index(
                fields=["tenant", "is_active"], name="idx_webhook_tenant_active"
            ),
            # Index for event queries
            models.Index(fields=["events"], name="idx_webhook_events"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.tenant.code})"

    def clean(self):
        """
        Validate webhook endpoint
        """
        # Validate URL
        try:
            URLValidator()(self.url)
        except ValidationError:
            raise ValidationError("Invalid webhook URL")

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # SECRET MANAGEMENT
    # ========================================================================

    def generate_secret(self):
        """
        Generate HMAC secret for webhook signing

        Returns:
            String secret

        Example:
            secret = webhook.generate_secret()
            # Returns: 'whsec_xxxxx...'
        """
        secret = f"whsec_{secrets.token_urlsafe(32)}"
        self.secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        self.save(update_fields=["secret_hash"])
        return secret

    def verify_signature(self, payload, signature):
        """
        Verify webhook signature

        Args:
            payload: Request body (bytes or string)
            signature: X-Webhook-Signature header value

        Returns:
            Boolean

        Example:
            if webhook.verify_signature(payload, signature):
                # Signature is valid
        """
        if not self.secret_hash:
            return False

        # Convert payload to bytes if needed
        if isinstance(payload, str):
            payload = payload.encode()

        # Extract signature from header (format: "sha256=xxx")
        if not signature or "=" not in signature:
            return False

        _, provided_sig = signature.split("=", 1)

        # Compute expected signature
        # Note: In production, use the original secret, not the hash
        # This is a simplified example
        expected_sig = hmac.new(
            self.secret_hash.encode(), payload, hashlib.sha256
        ).hexdigest()

        # Constant-time comparison
        return hmac.compare_digest(provided_sig, expected_sig)

    # ========================================================================
    # EVENT METHODS
    # ========================================================================

    def should_deliver_event(self, event_type):
        """
        Check if webhook should deliver this event

        Args:
            event_type: Event type (e.g., 'booking.created')

        Returns:
            Boolean

        Example:
            if webhook.should_deliver_event('booking.created'):
                # Send webhook
        """
        if not self.is_active:
            return False

        # Check if event is in subscribed events
        if "*" in self.events:
            return True  # Subscribe to all events

        return event_type in self.events

    def add_event(self, event_type):
        """
        Add event to subscription

        Args:
            event_type: Event type

        Example:
            webhook.add_event('booking.created')
        """
        if event_type not in self.events:
            self.events.append(event_type)
            self.save(update_fields=["events"])

    def remove_event(self, event_type):
        """
        Remove event from subscription

        Args:
            event_type: Event type

        Example:
            webhook.remove_event('booking.created')
        """
        if event_type in self.events:
            self.events.remove(event_type)
            self.save(update_fields=["events"])

    def update_events(self, events):
        """
        Update all subscribed events

        Args:
            events: List of event types

        Example:
            webhook.update_events(['booking.created', 'booking.updated'])
        """
        self.events = events
        self.save(update_fields=["events"])

    # ========================================================================
    # DELIVERY METHODS
    # ========================================================================

    def send_event(self, event_type, data, attempt=1):
        """
        Send webhook event

        Args:
            event_type: Event type
            data: Event data
            attempt: Attempt number

        Returns:
            WebhookDelivery instance

        Example:
            delivery = webhook.send_event('booking.created', {'id': 123})
        """
        # Check if webhook should deliver this event
        if not self.should_deliver_event(event_type):
            return None

        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=self,
            event_type=event_type,
            payload=json.dumps(data),
            attempt=attempt,
        )

        # Send webhook (async in production)
        delivery.send()

        return delivery

    def get_deliveries(self, limit=10, status=None):
        """
        Get webhook delivery history

        Args:
            limit: Maximum number of deliveries
            status: Filter by status (success, failed, pending)

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            deliveries = webhook.get_deliveries(limit=20, status='failed')
        """
        query = self.deliveries.all().order_by("-created_at")

        if status:
            query = query.filter(status=status)

        return query[:limit]

    def get_delivery_stats(self):
        """
        Get delivery statistics

        Returns:
            Dictionary with stats

        Example:
            stats = webhook.get_delivery_stats()
            # Returns: {
            #     'total': 100,
            #     'success': 95,
            #     'failed': 5,
            #     'success_rate': 95.0
            # }
        """
        from django.db.models import Count, Q

        total = self.deliveries.count()
        success = self.deliveries.filter(status="success").count()
        failed = self.deliveries.filter(status="failed").count()

        success_rate = (success / total * 100) if total > 0 else 0

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": success_rate,
        }
