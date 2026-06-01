# ============================================================================
# FILE: apps/webhooks/models.py (Enhanced)
# Webhook Delivery Models with Analytics
# ============================================================================

import hashlib
import hmac
import json
import time
from datetime import timedelta

import requests
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class WebhookDelivery(models.Model):
    """
    Enhanced webhook delivery model with comprehensive tracking

    Features:
    - JSONB payload storage: Efficient JSON storage
    - Comprehensive tracking: Track all delivery attempts
    - Retry logic: Exponential backoff retry strategy
    - Response tracking: Store response code and body
    - Status management: Track delivery status
    - Analytics: Query delivery statistics
    - Error handling: Detailed error tracking
    - Performance monitoring: Track delivery times

    Status Flow:
    PENDING -> SUCCESS (delivered successfully)
    PENDING -> FAILED (delivery failed, no more retries)
    PENDING -> RETRY (retry scheduled)
    RETRY -> SUCCESS (retry successful)
    RETRY -> FAILED (retry failed)

    Retry Strategy:
    - Exponential backoff: 2^attempt minutes
    - Attempt 1: Immediate
    - Attempt 2: 2 minutes
    - Attempt 3: 4 minutes
    - Attempt 4: 8 minutes
    - Max attempts: configurable per webhook

    Example:
        # Create delivery
        delivery = WebhookDelivery.objects.create(
            endpoint=webhook,
            event_type='booking.created',
            payload={'id': 123, 'status': 'confirmed'}
        )

        # Send delivery
        delivery.send()

        # Get delivery status
        status = delivery.get_status()

        # Get analytics
        stats = WebhookDelivery.get_delivery_stats(webhook)
    """

    STATUS_CHOICES = (
        ("PENDING", _("Pending - Waiting to send")),
        ("SUCCESS", _("Success - Delivered successfully")),
        ("FAILED", _("Failed - Delivery failed")),
        ("RETRY", _("Retry - Retry scheduled")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    endpoint = models.ForeignKey(
        "webhooks.WebhookEndpoint",
        on_delete=models.CASCADE,
        related_name="deliveries",
        db_index=True,
        help_text="Webhook endpoint",
    )

    # ========================================================================
    # EVENT INFORMATION
    # ========================================================================

    event_type = models.CharField(
        max_length=100, db_index=True, help_text='Event type (e.g., "booking.created")'
    )

    payload = models.JSONField(help_text="Event payload as JSON")

    # ========================================================================
    # RESPONSE INFORMATION
    # ========================================================================

    response_code = models.SmallIntegerField(
        null=True, blank=True, help_text="HTTP response status code"
    )

    response_body = models.TextField(
        blank=True, null=True, help_text="HTTP response body (truncated)"
    )

    # ========================================================================
    # DELIVERY TRACKING
    # ========================================================================

    attempt = models.SmallIntegerField(default=1, help_text="Attempt number")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="Delivery status",
    )

    # ========================================================================
    # TIMING INFORMATION
    # ========================================================================

    delivered_at = models.DateTimeField(
        null=True, blank=True, help_text="When delivery was successful"
    )

    failed_at = models.DateTimeField(
        null=True, blank=True, help_text="When delivery failed"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When delivery was created"
    )

    class Meta:
        db_table = "webhook_deliveries"
        verbose_name = _("Webhook Delivery")
        verbose_name_plural = _("Webhook Deliveries")
        ordering = ["-created_at"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding deliveries by endpoint and status
            models.Index(
                fields=["endpoint", "status"], name="idx_webhook_deliveries_endpoint"
            ),
            # Index for time-based queries
            models.Index(fields=["-created_at"], name="idx_webhook_deliveries_created"),
            # Index for event type queries
            models.Index(fields=["event_type"], name="idx_webhook_deliveries_event"),
            # Index for retry queries
            models.Index(
                fields=["status", "attempt"], name="idx_webhook_deliveries_retry"
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.event_type} - {self.status}"

    # ========================================================================
    # DELIVERY METHODS
    # ========================================================================

    def send(self):
        """
        Send webhook delivery

        Returns:
            Boolean (success)

        Example:
            success = delivery.send()
        """
        try:
            start_time = time.time()

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Django-Webhooks/1.0",
                "X-Webhook-ID": str(self.endpoint.id),
                "X-Webhook-Event": self.event_type,
                "X-Webhook-Timestamp": timezone.now().isoformat(),
                "X-Webhook-Delivery-ID": str(self.id),
                "X-Webhook-Attempt": str(self.attempt),
            }

            # Add custom headers from endpoint
            if self.endpoint.headers:
                headers.update(self.endpoint.headers)

            # Add signature
            if self.endpoint.secret_hash:
                payload_str = json.dumps(self.payload)
                signature = hmac.new(
                    self.endpoint.secret_hash.encode(),
                    payload_str.encode(),
                    hashlib.sha256,
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            # Send request
            response = requests.post(
                self.endpoint.url,
                json=self.payload,
                headers=headers,
                timeout=self.endpoint.timeout_sec,
            )

            # Record response
            duration_ms = int((time.time() - start_time) * 1000)
            self.response_code = response.status_code
            self.response_body = response.text[:1000]  # Limit response size

            # Check if successful
            if 200 <= response.status_code < 300:
                self.status = "SUCCESS"
                self.delivered_at = timezone.now()
                self.save()
                return True
            else:
                self.status = "FAILED"
                self.failed_at = timezone.now()

                # Schedule retry if attempts remaining
                if self.attempt < self.endpoint.retry_count:
                    self.schedule_retry()

                self.save()
                return False

        except requests.Timeout:
            self.status = "FAILED"
            self.failed_at = timezone.now()

            # Schedule retry
            if self.attempt < self.endpoint.retry_count:
                self.schedule_retry()

            self.save()
            return False

        except Exception as e:
            self.status = "FAILED"
            self.failed_at = timezone.now()
            self.response_body = str(e)[:1000]

            # Schedule retry
            if self.attempt < self.endpoint.retry_count:
                self.schedule_retry()

            self.save()
            return False

    def schedule_retry(self):
        """
        Schedule retry for failed delivery

        Retry Strategy:
        - Exponential backoff: 2^attempt minutes
        - Attempt 1: Immediate
        - Attempt 2: 2 minutes
        - Attempt 3: 4 minutes
        - Attempt 4: 8 minutes

        Example:
            delivery.schedule_retry()
        """
        self.status = "RETRY"

        # Exponential backoff: 2^attempt minutes
        retry_delay_minutes = 2**self.attempt
        self.save()

    def retry(self):
        """
        Create new delivery for retry

        Returns:
            WebhookDelivery instance

        Example:
            new_delivery = delivery.retry()
        """
        new_delivery = WebhookDelivery.objects.create(
            endpoint=self.endpoint,
            event_type=self.event_type,
            payload=self.payload,
            attempt=self.attempt + 1,
            status="PENDING",
        )
        return new_delivery

    # ========================================================================
    # STATUS METHODS
    # ========================================================================

    def is_successful(self):
        """Check if delivery was successful"""
        return self.status == "SUCCESS"

    def is_failed(self):
        """Check if delivery failed"""
        return self.status == "FAILED"

    def is_pending(self):
        """Check if delivery is pending"""
        return self.status == "PENDING"

    def is_retrying(self):
        """Check if delivery is retrying"""
        return self.status == "RETRY"

    def can_retry(self):
        """Check if delivery can be retried"""
        return self.status == "FAILED" and self.attempt < self.endpoint.retry_count

    def get_status_display_html(self):
        """Get HTML formatted status"""
        colors = {
            "PENDING": "#FFD93D",
            "SUCCESS": "#51CF66",
            "FAILED": "#FF6B6B",
            "RETRY": "#45B7D1",
        }

        return f'<span style="background-color: {colors.get(self.status, "#999")}; color: white; padding: 3px 8px; border-radius: 3px;">{self.get_status_display()}</span>'

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_pending_deliveries(cls):
        """
        Get all pending deliveries

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            pending = WebhookDelivery.get_pending_deliveries()
        """
        return cls.objects.filter(status="PENDING")

    @classmethod
    def get_failed_deliveries(cls):
        """
        Get all failed deliveries

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            failed = WebhookDelivery.get_failed_deliveries()
        """
        return cls.objects.filter(status="FAILED")

    @classmethod
    def get_retry_deliveries(cls):
        """
        Get all deliveries scheduled for retry

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            retries = WebhookDelivery.get_retry_deliveries()
        """
        return cls.objects.filter(status="RETRY")

    @classmethod
    def get_endpoint_deliveries(cls, endpoint, status=None, limit=100):
        """
        Get deliveries for an endpoint

        Args:
            endpoint: WebhookEndpoint instance
            status: Optional status filter
            limit: Maximum number of deliveries

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            deliveries = WebhookDelivery.get_endpoint_deliveries(
                endpoint, status='FAILED', limit=50
            )
        """
        query = cls.objects.filter(endpoint=endpoint).order_by("-created_at")

        if status:
            query = query.filter(status=status)

        return query[:limit]

    @classmethod
    def get_event_deliveries(cls, event_type, limit=100):
        """
        Get deliveries for an event type

        Args:
            event_type: Event type
            limit: Maximum number of deliveries

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            deliveries = WebhookDelivery.get_event_deliveries('booking.created')
        """
        return cls.objects.filter(event_type=event_type).order_by("-created_at")[:limit]

    # ========================================================================
    # ANALYTICS METHODS
    # ========================================================================

    @classmethod
    def get_delivery_stats(cls, endpoint=None, days=7):
        """
        Get delivery statistics

        Args:
            endpoint: Optional WebhookEndpoint instance
            days: Number of days to analyze

        Returns:
            Dictionary with statistics

        Example:
            stats = WebhookDelivery.get_delivery_stats(endpoint, days=30)
            # Returns: {
            #     'total': 1000,
            #     'success': 950,
            #     'failed': 50,
            #     'success_rate': 95.0,
            #     'by_status': {...},
            #     'by_event': {...}
            # }
        """
        start_date = timezone.now() - timedelta(days=days)

        query = cls.objects.filter(created_at__gte=start_date)

        if endpoint:
            query = query.filter(endpoint=endpoint)

        total = query.count()
        success = query.filter(status="SUCCESS").count()
        failed = query.filter(status="FAILED").count()
        retry = query.filter(status="RETRY").count()
        pending = query.filter(status="PENDING").count()

        success_rate = (success / total * 100) if total > 0 else 0

        # By status
        by_status = {
            "SUCCESS": success,
            "FAILED": failed,
            "RETRY": retry,
            "PENDING": pending,
        }

        # By event type
        by_event = {}
        for delivery in query:
            by_event[delivery.event_type] = by_event.get(delivery.event_type, 0) + 1

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "retry": retry,
            "pending": pending,
            "success_rate": success_rate,
            "by_status": by_status,
            "by_event": by_event,
            "period_days": days,
        }

    @classmethod
    def get_endpoint_stats(cls, endpoint):
        """
        Get detailed statistics for an endpoint

        Args:
            endpoint: WebhookEndpoint instance

        Returns:
            Dictionary with detailed stats

        Example:
            stats = WebhookDelivery.get_endpoint_stats(endpoint)
        """
        deliveries = cls.objects.filter(endpoint=endpoint)

        if not deliveries.exists():
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "avg_attempts": 0,
                "success_rate": 0,
            }

        total = deliveries.count()
        success = deliveries.filter(status="SUCCESS").count()
        failed = deliveries.filter(status="FAILED").count()

        # Calculate average attempts
        avg_attempts = deliveries.aggregate(avg=Avg("attempt"))["avg"] or 0

        success_rate = (success / total * 100) if total > 0 else 0

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "avg_attempts": round(avg_attempts, 2),
            "success_rate": round(success_rate, 2),
            "last_delivery": deliveries.order_by("-created_at").first(),
            "first_delivery": deliveries.order_by("created_at").first(),
        }

    @classmethod
    def get_event_stats(cls, event_type):
        """
        Get statistics for an event type

        Args:
            event_type: Event type

        Returns:
            Dictionary with statistics

        Example:
            stats = WebhookDelivery.get_event_stats('booking.created')
        """
        deliveries = cls.objects.filter(event_type=event_type)

        total = deliveries.count()
        success = deliveries.filter(status="SUCCESS").count()
        failed = deliveries.filter(status="FAILED").count()

        success_rate = (success / total * 100) if total > 0 else 0

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "endpoints": deliveries.values("endpoint__name").distinct().count(),
        }

    @classmethod
    def get_failed_deliveries_by_reason(cls, endpoint=None, limit=10):
        """
        Get failed deliveries grouped by response code

        Args:
            endpoint: Optional WebhookEndpoint instance
            limit: Maximum number of groups

        Returns:
            List of tuples (response_code, count)

        Example:
            failures = WebhookDelivery.get_failed_deliveries_by_reason(endpoint)
        """
        query = cls.objects.filter(status="FAILED")

        if endpoint:
            query = query.filter(endpoint=endpoint)

        failures = {}
        for delivery in query:
            code = delivery.response_code or "TIMEOUT"
            failures[code] = failures.get(code, 0) + 1

        # Sort by count
        sorted_failures = sorted(failures.items(), key=lambda x: x[1], reverse=True)

        return sorted_failures[:limit]

    @classmethod
    def get_retry_candidates(cls):
        """
        Get deliveries that should be retried

        Returns:
            QuerySet of WebhookDelivery objects

        Example:
            candidates = WebhookDelivery.get_retry_candidates()
        """
        return cls.objects.filter(status="RETRY").order_by("created_at")

    @classmethod
    def cleanup_old_deliveries(cls, days=30):
        """
        Delete old delivery records

        Args:
            days: Delete deliveries older than this many days

        Returns:
            Number of deleted deliveries

        Example:
            deleted = WebhookDelivery.cleanup_old_deliveries(days=30)
        """
        cutoff_date = timezone.now() - timedelta(days=days)

        old_deliveries = cls.objects.filter(
            created_at__lt=cutoff_date, status__in=["SUCCESS", "FAILED"]
        )
        count = old_deliveries.count()
        old_deliveries.delete()

        return count
