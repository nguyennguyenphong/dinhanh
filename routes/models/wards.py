from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Ward(BaseModel):
    """
    Ward model for sub-district organization

    Features:
    - District relationship: Link to district
    - Ward codes: Unique identifiers
    - Location management: Organize locations
    - Statistics: Track locations

    Example:
        # Create ward
        ward = Ward.objects.create(
            district=district,
            code='HN0101',
            name='Hang Trong'
        )

        # Get locations
        locations = ward.get_locations()
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    district = models.ForeignKey(
        "routes.District",
        on_delete=models.CASCADE,
        related_name="wards",
        db_index=True,
        help_text="District this ward belongs to",
    )

    # ========================================================================
    # WARD IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]+$",
                message="Code must contain only uppercase letters and numbers",
            )
        ],
        help_text="Ward code",
    )

    name = models.CharField(max_length=100, help_text="Ward name")

    class Meta:
        db_table = "wards"
        verbose_name = _("Ward")
        verbose_name_plural = _("Wards")
        ordering = ["district", "name"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique code per district
            models.UniqueConstraint(
                fields=["district", "code"], name="unique_district_ward_code"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for district queries
            models.Index(fields=["district"], name="idx_ward_district"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.district.code})"

    # ========================================================================
    # LOCATION METHODS
    # ========================================================================

    def get_locations(self):
        """
        Get all locations in ward

        Returns:
            QuerySet of Location objects

        Example:
            locations = ward.get_locations()
        """
        return self.locations.all().order_by("name")

    def get_location_count(self):
        """
        Get number of locations

        Returns:
            Integer

        Example:
            count = ward.get_location_count()
        """
        return self.locations.count()

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_by_province(cls, province):
        """
        Get all wards in province

        Args:
            province: Province instance

        Returns:
            QuerySet of Ward objects

        Example:
            wards = Ward.get_by_province(province)
        """
        return cls.objects.filter(district__province=province).order_by(
            "district", "name"
        )
