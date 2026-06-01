from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class District(models.Model):
    """
    District model for sub-provincial organization

    Features:
    - Province relationship: Link to province
    - District codes: Unique identifiers
    - Ward management: Organize wards
    - Statistics: Track wards and locations

    Example:
        # Create district
        district = District.objects.create(
            province=province,
            code='HN01',
            name='Hoan Kiem'
        )

        # Get wards
        wards = district.get_wards()

        # Get statistics
        stats = district.get_statistics()
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    province = models.ForeignKey(
        "routes.Province",
        on_delete=models.CASCADE,
        related_name="districts",
        db_index=True,
        help_text="Province this district belongs to",
    )

    # ========================================================================
    # DISTRICT IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]+$",
                message="Code must contain only uppercase letters and numbers",
            )
        ],
        help_text="District code",
    )

    name = models.CharField(max_length=100, help_text="District name")

    class Meta:
        db_table = "districts"
        verbose_name = _("District")
        verbose_name_plural = _("Districts")
        ordering = ["province", "name"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique code per province
            models.UniqueConstraint(
                fields=["province", "code"], name="unique_province_district_code"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for province queries
            models.Index(fields=["province"], name="idx_district_province"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.province.code})"

    # ========================================================================
    # WARD METHODS
    # ========================================================================

    def get_wards(self):
        """
        Get all wards in district

        Returns:
            QuerySet of Ward objects

        Example:
            wards = district.get_wards()
        """
        return self.wards.all().order_by("name")

    def get_ward_count(self):
        """
        Get number of wards

        Returns:
            Integer

        Example:
            count = district.get_ward_count()
        """
        return self.wards.count()

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    def get_statistics(self):
        """
        Get district statistics

        Returns:
            Dictionary with statistics

        Example:
            stats = district.get_statistics()
        """
        from .locations import Location
        wards = self.wards.count()
        locations = Location.objects.filter(ward__district=self).count()

        return {"wards": wards, "locations": locations}
