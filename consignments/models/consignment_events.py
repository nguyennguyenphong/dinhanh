# ============================================================================
# FILE: apps/logistics/models.py
# Cargo Logistics & Consignment Audit Trail Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class ConsignmentEvent(BaseModel):
    """
    ConsignmentEvent model acting as an immutable historical black-box ledger tracking cargo lifecycles.

    Features:
    - High-Fidelity Audit Trail: Cascade-linked directly to parent consignments for deep timeline tracking.
    - Specialized Event Taxonomy: Segregates actions into status mutations, manual annotations, scans, or photo uploads.
    - Historical State Mirroring: Captures delta status transitions (old vs new) to reconstruct historical tracking.
    - Operational Telemetry: Attributes exactly who (recorded_by), when (recorded_at), and where (location) an event occurred.

    Event Types:
    - STATUS_CHANGE: System or automated state transition (e.g., RECEIVED -> LOADED).
    - NOTE: Manual administrative or operational annotations added by station clerks or drivers.
    - SCAN: Hardware barcode/QR reader pings confirming physical presence at a facility floor layout.
    - PHOTO: Media attachment logs capturing parcel external packaging integrity snapshots.

    Example:
        # Log a physical scanner gun check-in event at a transit station counter hub
        event = ConsignmentEvent.objects.create(
            consignment_id=102482,
            event_type='SCAN',
            description='Handheld scanner #POS-04 verified package registration grid arrival.',
            location='Mien Dong Bus Station Terminal Counter 03',
            recorded_by=15
        )
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    EVENT_TYPE_CHOICES = (
        (
            "STATUS_CHANGE",
            _("Status Change - State mutation tracking timeline adjustments"),
        ),
        (
            "NOTE",
            _(
                "Note - Hand-written operational text memo or customer alert annotations"
            ),
        ),
        (
            "SCAN",
            _(
                "Scan - Hardware scanner laser gun ping logging warehouse floor checkpoint presence"
            ),
        ),
        (
            "PHOTO",
            _(
                "Photo - Optical imagery attachment asset tracking packaging structural integrity"
            ),
        ),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & DATA INTEGRITY CONNECTIONS
    # ========================================================================

    consignment = models.ForeignKey(
        "consignments.Consignment",
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True,
        help_text="The parent parcel transport ledger line being audited by this telemetry timestamp snapshot",
    )

    recorded_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        related_name="logged_consignment_events",
        null=True,
        blank=True,
        db_index=True,
        help_text="The employee profile account or system background daemon executing this tracking snapshot log",
    )

    # ========================================================================
    # EVENT TAXONOMY & METADATA ATTRIBUTES
    # ========================================================================

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        help_text="The primary structural action classification assigned to this timeline snapshot row",
    )

    old_status = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="The previous state string cloned from parent logs prior to executing mutations (e.g., RECEIVED)",
    )

    new_status = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="The target current state string mapped down onto the parent log (e.g., LOADED)",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Descriptive telemetry summaries or specific event context text data blocks (e.g., Packed inside Truck 29B-123.45)",
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Physical office text string or text description logging where the action executed",
    )

    # ========================================================================
    # CHRONOLOGY WINDOWS
    # ========================================================================

    recorded_at = models.DateTimeField(
        default=models.functions.Now,
        help_text="Timezone-aware timestamp logging exactly when this micro-action entered database storage frameworks",
    )

    class Meta:
        db_table = "consignment_events"
        verbose_name = _("Consignment Journey Event")
        verbose_name_plural = _("Consignment Journey Events")

        # Default application-layer ordering matches index lookup specifications
        ordering = ["consignment", "-recorded_at"]

        # ====================================================================
        # COMPOSITE PRODUCTION INDEXES & CONSTRAINTS
        # ====================================================================

        indexes = [
            # Replicates exact structure of CREATE INDEX idx_consignment_events ON consignment_events(consignment_id, recorded_at DESC);
            models.Index(
                fields=["consignment", "-recorded_at"], name="idx_consignment_events"
            )
        ]

        constraints = [
            # Direct database CHECK constraint restricting event classifications parameters
            models.CheckConstraint(
                condition=models.Q(
                    event_type__in=["STATUS_CHANGE", "NOTE", "SCAN", "PHOTO"]
                ),
                name="chk_consignment_event_type_enum",
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Consignment #{self.consignment_id} Event: {self.event_type} at {self.recorded_at.strftime('%Y-%m-%d %H:%M:%S')}"

    # ========================================================================
    # PRODUCTION COMPLIANCE & STATE TRANSITION CONTEXT CAPTURE METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer data schema structural alignment validation rules.
        """
        super().clean()

        # If the event type is flagged as a status transition, enforce historical state log visibility
        if self.event_type == "STATUS_CHANGE" and not self.new_status:
            raise ValidationError(
                {
                    "new_status": _(
                        "Compliance Discrepancy: Type is marked STATUS_CHANGE but no target new_status code parameter is provided."
                    )
                }
            )
