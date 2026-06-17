# ============================================================================
# FILE: apps/logistics/models.py
# Cargo Logistics & Manifest Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class ConsignmentManifest(BaseModel):
    """
    ConsignmentManifest model representing the official consolidated cargo transit manifest document.

    Features:
    - Master Bulk Dispatch: Aggregates multiple separate individual parcels into a single batch file for a specific trip.
    - Unique Barcode/Code Indexing: Enforces system-wide unique tracking codes for quick multi-parcel yard scanning.
    - Personnel Allocation Auditing: Tracks the exact employee account responsible for assembling and closing the batch.

    Statuses:
    - OPEN: Active manifest workspace. Clerks are currently scanning, adding, or removing parcels into the vehicle deck.
    - CLOSED: Package collection completed, weights/volumes sealed, cargo manifest locked against modifications.
    - DISPATCHED: Vehicle has officially departed the terminal yard gate, manifest is actively transit on-route.

    Example:
        # Open a new manifest sheet for a night shift trip departure
        manifest = ConsignmentManifest.objects.create(
            manifest_code='MNF-20260530-K789',
            trip_id=4512,
            created_by=24,
            status='OPEN'
        )
    """

    STATUS_CHOICES = (
        (
            "OPEN",
            _(
                "Open - Active batching workspace, accepting package additions and scans"
            ),
        ),
        (
            "CLOSED",
            _(
                "Closed - Sealed batch sheet, cargo locked, awaiting yard driver gate release"
            ),
        ),
        (
            "DISPATCHED",
            _(
                "Dispatched - Vehicle cleared terminal gates, manifest is actively in transit"
            ),
        ),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & DATA INTEGRITY CONNECTIONS
    # ========================================================================

    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.PROTECT,  # Production safety: strict PROTECT blocks deleting core trips if freight manifests depend on it
        related_name="consignment_manifests",
        db_index=True,
        help_text="The specific active vehicle fleet journey assigned to physically transport this consolidated batch",
    )

    created_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name="created_manifests",
        null=True,
        blank=True,
        db_index=True,
        help_text="The specific logistics officer or warehouse clerk who compiled and authorized the cargo loading sheet",
    )

    # ========================================================================
    # IDENTITY CODE & MANIFEST METADATA
    # ========================================================================

    manifest_code = models.CharField(
        max_length=30,
        unique=True,  # Matches VARCHAR(30) NOT NULL UNIQUE
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Manifest tracking code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique human-readable system manifest identity string token (e.g., MNF-HANOI-2026-X9A)",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",  # Matches NOT NULL DEFAULT 'OPEN'
        db_index=True,
        help_text="The operational validation phase tracking this aggregated shipment listing through transport loops",
    )

    class Meta:
        db_table = "consignment_manifests"
        verbose_name = _("Consignment Manifest")
        verbose_name_plural = _("Consignment Manifests")
        ordering = ["-created_at", "manifest_code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(status__in=["OPEN", "CLOSED", "DISPATCHED"]),
                name="chk_consignment_manifest_status_rules",
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Manifest [{self.manifest_code}] | Trip #{self.trip_id} [{self.status}]"

    # ========================================================================
    # ENTERPRISE LOGISTICS WORKFLOW & STATE TRANSITION ENGINES
    # ========================================================================

    def clean(self):
        """
        Application-layer validation auditing schema data integrity constraints before commit.
        """
        super().clean()

    def execute_manifest_closure(self):
        """
        Locks and seals the current manifest sheet. Validates that it contains cargo components,
        freezes data payload parameters, and shifts status phase to CLOSED.
        """
        if self.status != "OPEN":
            raise ValidationError(
                _(
                    "Logistics Exception: Seal/Closure operations can only trigger on active OPEN workspace manifests."
                )
            )

        # Production Safety: Verify that there are actually parcels attached to this manifest before sealing
        # Assuming a Reverse-FK link exists from Consignment model (e.g., consignment.manifest = models.ForeignKey(ConsignmentManifest))
        if not self.consignments.exists():
            raise ValidationError(
                _(
                    "Operations Error: Cannot close an empty manifest sheet. Scan or assign parcels to vehicle load grids first."
                )
            )

        self.status = "CLOSED"
        self.save(update_fields=["status"])

    def execute_gate_dispatch(self):
        """
        Transitions the closed manifest document into the final active transit state (DISPATCHED)
        as the transport fleet vehicle departs the terminal yard checkpoints.
        """
        if self.status != "CLOSED":
            raise ValidationError(
                _(
                    "Logistics Exception: Gate release protocols require the target manifest document to be fully CLOSED and sealed."
                )
            )

        self.status = "DISPATCHED"
        self.save(update_fields=["status"])

        # Core Cascade Automation Trigger: Automatically loop and upgrade all inner related separate
        # Consignment parcel states to 'IN_TRANSIT' simultaneously, ensuring global system synchronization.
        self.consignments.all().update(status="IN_TRANSIT")
