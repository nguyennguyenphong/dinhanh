# ============================================================================
# FILE: apps/locations/models.py
# Province, District, Ward Models
# ============================================================================

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class Province(SafeDeleteModel):
    """
    Province model for geographical organization

    Features:
    - Province codes: Unique identifiers
    - Region classification: NORTH, CENTRAL, SOUTH
    - District management: Organize districts
    - Query optimization: Efficient location queries
    - Statistics: Track locations in province

    Regions:
    - NORTH: Northern provinces
    - CENTRAL: Central provinces
    - SOUTH: Southern provinces

    Example:
        # Create province
        province = Province.objects.create(
            code='HN',
            name='Hanoi',
            region='NORTH'
        )

        # Get districts
        districts = province.get_districts()

        # Get statistics
        stats = province.get_statistics()
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    REGION_CHOICES = (
        ("NORTH", _("North - Northern region")),
        ("CENTRAL", _("Central - Central region")),
        ("SOUTH", _("South - Southern region")),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # PROVINCE IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]+$",
                message="Code must contain only uppercase letters and numbers",
            )
        ],
        help_text="Province code (e.g., HN, HCM, DN)",
    )

    name = models.CharField(max_length=100, help_text="Province name")

    # ========================================================================
    # REGION CLASSIFICATION
    # ========================================================================

    region = models.CharField(
        max_length=30,
        choices=REGION_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text="Geographic region",
    )

    class Meta:
        db_table = "provinces"
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")
        ordering = ["region", "name"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for region queries
            models.Index(fields=["region"], name="idx_province_region"),
            # Index for code lookup
            models.Index(fields=["code"], name="idx_province_code"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.code})"

    # ========================================================================
    # DISTRICT METHODS
    # ========================================================================

    def get_districts(self):
        """
        Get all districts in province

        Returns:
            QuerySet of District objects

        Example:
            districts = province.get_districts()
        """
        return self.districts.all().order_by("name")

    def get_district_count(self):
        """
        Get number of districts

        Returns:
            Integer

        Example:
            count = province.get_district_count()
        """
        return self.districts.count()

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    def get_statistics(self):
        """
        Get province statistics

        Returns:
            Dictionary with statistics

        Example:
            stats = province.get_statistics()
            # Returns: {
            #     'districts': 12,
            #     'wards': 145,
            #     'locations': 500
            # }
        """
        from django.apps import apps

        Ward = apps.get_model("locations", "Ward")
        Location = apps.get_model("locations", "Location")

        districts = self.districts.count()
        wards = Ward.objects.filter(district__province=self).count()
        locations = Location.objects.filter(ward__district__province=self).count()

        return {"districts": districts, "wards": wards, "locations": locations}

    @classmethod
    def get_by_region(cls, region):
        """
        Get provinces by region

        Args:
            region: Region code (NORTH, CENTRAL, SOUTH)

        Returns:
            QuerySet of Province objects

        Example:
            northern = Province.get_by_region('NORTH')
        """
        return cls.objects.filter(region=region).order_by("name")

    @classmethod
    def get_all_regions(cls):
        """
        Get all regions with provinces

        Returns:
            Dictionary with regions and provinces

        Example:
            regions = Province.get_all_regions()
        """
        regions = {}
        for region_code, region_name in cls.REGION_CHOICES:
            regions[region_code] = {
                "name": region_name,
                "provinces": cls.objects.filter(region=region_code),
            }
        return regions
