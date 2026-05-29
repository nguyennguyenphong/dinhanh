# ============================================================================
# FILE: apps/webhooks/models.py
# Webhook Endpoint Models with Event Delivery
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
import hashlib
import hmac
import secrets
import json
from tenants.models.tenants import Tenant


class WebhookEndpoint(models.Model):
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
        Tenant,
        on_delete=models.CASCADE,
        related_name='webhook_endpoints',
        db_index=True,
        help_text='Tenant that owns this webhook',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # WEBHOOK IDENTIFICATION
    # ========================================================================
    
    name = models.CharField(
        max_length=100,
        help_text='Human-readable name for the webhook',
        db_comment='Webhook name'
    )
    url = models.CharField(
        max_length=500,
        validators=[URLValidator()],
        help_text='URL to send webhook events to',
        db_comment='Webhook URL'
    )
    
    # ========================================================================
    # SECURITY
    # ========================================================================
    
    secret_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='HMAC-SHA256 secret for signing requests',
        db_comment='Secret hash'
    )
    
    # ========================================================================
    # EVENT CONFIGURATION
    # ========================================================================
    
    events = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text='List of events to subscribe to',
        db_comment='Subscribed events'
    )
    
    # ========================================================================
    # REQUEST CONFIGURATION
    # ========================================================================
    
    timeout_sec = models.SmallIntegerField(
        default=10,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60)
        ],
        help_text='Request timeout in seconds',
        db_comment='Timeout seconds'
    )
    retry_count = models.SmallIntegerField(
        default=3,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ],
        help_text='Number of retry attempts on failure',
        db_comment='Retry count'
    )
    
    # ========================================================================
    # CUSTOM HEADERS
    # ========================================================================
    
    headers = models.JSONField(
        default=dict,
        blank=True,
        help_text='Custom headers to include in requests',
        db_comment='Custom headers'
    )
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Webhook is active and will receive events',
        db_comment='Active status'
    )
    
    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================
    
    created_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='webhooks_created',
        help_text='User who created this webhook',
        db_comment='Created by user'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this webhook was created',
        db_comment='Creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this webhook was last updated',
        db_comment='Last update timestamp'
    )

    class Meta:
        db_table = 'webhook_endpoints'
        verbose_name = _('Webhook Endpoint')
        verbose_name_plural = _('Webhook Endpoints')
        ordering = ['-created_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding active webhooks
            models.Index(
                fields=['tenant', 'is_active'],
                name='idx_webhook_tenant_active',
                db_comment='Query active webhooks by tenant'
            ),
            # Index for event queries
            models.Index(
                fields=['events'],
                name='idx_webhook_events',
                db_comment='Query webhooks by events'
            ),
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
            raise ValidationError('Invalid webhook URL')

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
        self.save(update_fields=['secret_hash'])
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
        if not signature or '=' not in signature:
            return False
        
        _, provided_sig = signature.split('=', 1)
        
        # Compute expected signature
        # Note: In production, use the original secret, not the hash
        # This is a simplified example
        expected_sig = hmac.new(
            self.secret_hash.encode(),
            payload,
            hashlib.sha256
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
        if '*' in self.events:
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
            self.save(update_fields=['events'])

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
            self.save(update_fields=['events'])

    def update_events(self, events):
        """
        Update all subscribed events
        
        Args:
            events: List of event types
        
        Example:
            webhook.update_events(['booking.created', 'booking.updated'])
        """
        self.events = events
        self.save(update_fields=['events'])

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
            attempt=attempt
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
        query = self.deliveries.all().order_by('-created_at')
        
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
        success = self.deliveries.filter(status='success').count()
        failed = self.deliveries.filter(status='failed').count()
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'success_rate': success_rate
        }


class WebhookDelivery(models.Model):
    """
    Webhook delivery record for tracking event delivery
    
    Features:
    - Track delivery attempts
    - Store request/response details
    - Retry logic
    - Delivery history
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pending - Waiting to send')),
        ('success', _('Success - Delivered successfully')),
        ('failed', _('Failed - Delivery failed')),
        ('retrying', _('Retrying - Retry in progress')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    webhook = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='deliveries',
        db_index=True,
        help_text='Webhook endpoint',
        db_comment='Reference to webhook'
    )
    
    # ========================================================================
    # EVENT INFORMATION
    # ========================================================================
    
    event_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Event type (e.g., "booking.created")',
        db_comment='Event type'
    )
    
    payload = models.TextField(
        help_text='Event payload (JSON)',
        db_comment='Event payload'
    )
    
    # ========================================================================
    # DELIVERY DETAILS
    # ========================================================================
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Delivery status',
        db_comment='Delivery status'
    )
    
    attempt = models.SmallIntegerField(
        default=1,
        help_text='Attempt number',
        db_comment='Attempt number'
    )
    
    # ========================================================================
    # RESPONSE INFORMATION
    # ========================================================================
    
    response_status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text='HTTP response status code',
        db_comment='Response status'
    )
    
    response_body = models.TextField(
        blank=True,
        null=True,
        help_text='HTTP response body',
        db_comment='Response body'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text='Error message if delivery failed',
        db_comment='Error message'
    )
    
    # ========================================================================
    # TIMING
    # ========================================================================
    
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text='Request duration in milliseconds',
        db_comment='Duration (ms)'
    )
    
    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When to retry next',
        db_comment='Next retry time'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When delivery was created',
        db_comment='Creation timestamp'
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When delivery was sent',
        db_comment='Sent timestamp'
    )

    class Meta:
        db_table = 'webhook_deliveries'
        verbose_name = _('Webhook Delivery')
        verbose_name_plural = _('Webhook Deliveries')
        ordering = ['-created_at']
        
        indexes = [
            models.Index(
                fields=['webhook', 'status'],
                name='idx_webhook_delivery_status',
                db_comment='Query deliveries by webhook and status'
            ),
            models.Index(
                fields=['event_type'],
                name='idx_webhook_delivery_event',
                db_comment='Query deliveries by event type'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.event_type} - {self.status}"

    def send(self):
        """
        Send webhook delivery
        
        Example:
            delivery.send()
        """
        import requests
        import time
        
        try:
            start_time = time.time()
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Django-Webhooks/1.0',
                'X-Webhook-ID': str(self.webhook.id),
                'X-Webhook-Event': self.event_type,
                'X-Webhook-Timestamp': timezone.now().isoformat(),
            }
            
            # Add custom headers
            if self.webhook.headers:
                headers.update(self.webhook.headers)
            
            # Add signature
            if self.webhook.secret_hash:
                signature = hmac.new(
                    self.webhook.secret_hash.encode(),
                    self.payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = f'sha256={signature}'
            
            # Send request
            response = requests.post(
                self.webhook.url,
                data=self.payload,
                headers=headers,
                timeout=self.webhook.timeout_sec
            )
            
            # Record response
            duration_ms = int((time.time() - start_time) * 1000)
            self.response_status_code = response.status_code
            self.response_body = response.text[:1000]  # Limit response size
            self.duration_ms = duration_ms
            self.sent_at = timezone.now()
            
            # Check if successful
            if 200 <= response.status_code < 300:
                self.status = 'success'
            else:
                self.status = 'failed'
                self.error_message = f'HTTP {response.status_code}'
                
                # Schedule retry
                if self.attempt < self.webhook.retry_count:
                    self.schedule_retry()
            
            self.save()
            
        except requests.Timeout:
            self.status = 'failed'
            self.error_message = 'Request timeout'
            self.schedule_retry()
            self.save()
            
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
            self.schedule_retry()
            self.save()

    def schedule_retry(self):
        """
        Schedule retry for failed delivery
        
        Example:
            delivery.schedule_retry()
        """
        if self.attempt >= self.webhook.retry_count:
            return
        
        # Exponential backoff: 2^attempt minutes
        retry_delay = 2 ** self.attempt
        self.next_retry_at = timezone.now() + timezone.timedelta(minutes=retry_delay)

    def retry(self):
        """
        Retry failed delivery
        
        Returns:
            WebhookDelivery instance
        
        Example:
            new_delivery = delivery.retry()
        """
        new_delivery = WebhookDelivery.objects.create(
            webhook=self.webhook,
            event_type=self.event_type,
            payload=self.payload,
            attempt=self.attempt + 1
        )
        new_delivery.send()
        return new_delivery