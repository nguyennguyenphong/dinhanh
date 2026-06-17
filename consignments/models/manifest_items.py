# ============================================================================
# FILE: apps/logistics/models.py
# Cargo Logistics & Manifest Junction Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class ManifestItem(BaseModel):
    """
    ManifestItem model acting as a strict high-performance relational bridge (Junction Table)
    mapping individual parcel consignments into master bulk trip manifests.

    Features:
    - Many-to-Many Breakdown: Links discrete cargo packages explicitly to an organized vehicle dispatch file.
    - Idempotency / Double Loading Protection: Enforces strict database-level unique constraints preventing
      the same parcel from being scanned into the same vehicle manifest duplicate times.
    - Operational Telemetry Auditing: Tracks the exact timezone-aware timestamp when the item was packed.

    Example:
        # Link a physical parcel into a sealed vehicle loading manifest layout
        item = ManifestItem.objects.create(
            manifest_id=45,
            consignment_id=100293
        )
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & NETWORK TOPOLOGY LINKS
    # ========================================================================

    manifest = models.ForeignKey(
        "consignments.ConsignmentManifest",
        on_delete=models.CASCADE,  # Matches REFERENCES consignment_manifests(id) ON DELETE CASCADE
        related_name="manifest_items",
        db_index=True,
        help_text="The parent batch manifest document compiling this cargo structural entry lines",
    )

    consignment = models.ForeignKey(
        "consignments.Consignment",
        on_delete=models.PROTECT,  # Production safety: block deleting parcel records if they are already historically tracked inside a manifest
        related_name="manifest_links",
        db_index=True,
        help_text="The explicit separate cargo package object being packed into the vehicle deck space",
    )

    # ========================================================================
    # CHRONOLOGY AUDIT MARKS
    # ========================================================================

    loaded_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at execution layer
        help_text="Timezone-aware timestamp logging exactly when the warehouse laser gun scanned this item into the trip batch",
    )

    class Meta:
        db_table = "manifest_items"
        verbose_name = _("Manifest Cargo Item")
        verbose_name_plural = _("Manifest Cargo Items")
        ordering = ["manifest", "-loaded_at"]

        # ====================================================================
        # CONSTRAINTS & UNIQUE INDEXES
        # ====================================================================

        constraints = [
            # Replicates exact structure of UNIQUE (manifest_id, consignment_id)
            models.UniqueConstraint(
                fields=["manifest", "consignment"], name="uq_manifest_consignment_item"
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Manifest #{self.manifest_id} -> Cargo #{self.consignment_id} (Loaded: {self.loaded_at.strftime('%H:%M:%S')})"

    # ========================================================================
    # LOGISTICS INTEGRITY & WORKFLOW GATEWAYS
    # ========================================================================

    def clean(self):
        """
        Application-layer workflow checks preventing loading logistics violations.
        """
        super().clean()

        # 1. Verification Gate: Prevent adding items to a manifest that has already departed or been sealed
        if self.manifest_id and self.manifest.status != "OPEN":
            raise ValidationError(
                _(
                    "Logistics Security Error: Cannot add or load parcels into a manifest that is already CLOSED or DISPATCHED."
                )
            )

        # 2. Alignment Check: Force parent references to share identical cross-system parameters if applicable
        if self.manifest_id and self.consignment_id:
            # Synchronize parent trip linkage data to avoid routing anomalies
            if (
                self.consignment.trip_id
                and self.consignment.trip_id != self.manifest.trip_id
            ):
                raise ValidationError(
                    _(
                        "Routing Conflict: Target parcel is already routing scheduled for a different fleet journey transaction."
                    )
                )

    def save(self, *args, **kwargs):
        """
        Overridden save protocol ensuring automated transactional cascade state
        upgrades down onto parent logistics documents automatically.
        """
        # Execute business logic rules validations
        self.full_clean()

        is_creating = self._state.adding
        super().save(*args, **kwargs)

        if is_creating:
            # Cascade Update Engine: Automatically upgrade the child parcel tracking phase
            # to 'LOADED' and assign the corresponding trip_id index instantly upon scanning.
            self.consignment.trip = self.manifest.trip
            self.consignment.status = "LOADED"
            self.consignment.save(update_fields=["trip", "status", "updated_at"])
