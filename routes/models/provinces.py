# ============================================================================
# FILE: apps/locations/models.py
# Province, District, Ward Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db.models import Q


class Province(models.Model):
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

    REGION_CHOICES = (
        ('NORTH', _('North - Northern region')),
        ('CENTRAL', _('Central - Central region')),
        ('SOUTH', _('South - Southern region')),
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
                regex=r'^[A-Z0-9]+$',
                message='Code must contain only uppercase letters and numbers'
            )
        ],
        help_text='Province code (e.g., HN, HCM, DN)'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Province name'
    )
    
    # ========================================================================
    # REGION CLASSIFICATION
    # ========================================================================
    
    region = models.CharField(
        max_length=30,
        choices=REGION_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text='Geographic region'
    )

    class Meta:
        db_table = 'provinces'
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')
        ordering = ['region', 'name']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for region queries
            models.Index(
                fields=['region'],
                name='idx_province_region'
            ),
            # Index for code lookup
            models.Index(
                fields=['code'],
                name='idx_province_code'
            ),
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
        return self.districts.all().order_by('name')

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
        districts = self.districts.count()
        wards = Ward.objects.filter(district__province=self).count()
        locations = Location.objects.filter(ward__district__province=self).count()
        
        return {
            'districts': districts,
            'wards': wards,
            'locations': locations
        }

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
        return cls.objects.filter(region=region).order_by('name')

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
                'name': region_name,
                'provinces': cls.objects.filter(region=region_code)
            }
        return regions


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
        Province,
        on_delete=models.CASCADE,
        related_name='districts',
        db_index=True,
        help_text='Province this district belongs to'
    )
    
    # ========================================================================
    # DISTRICT IDENTIFICATION
    # ========================================================================
    
    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='Code must contain only uppercase letters and numbers'
            )
        ],
        help_text='District code'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='District name'
    )

    class Meta:
        db_table = 'districts'
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        ordering = ['province', 'name']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique code per province
            models.UniqueConstraint(
                fields=['province', 'code'],
                name='unique_province_district_code'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for province queries
            models.Index(
                fields=['province'],
                name='idx_district_province'
            ),
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
        return self.wards.all().order_by('name')

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
        wards = self.wards.count()
        locations = Location.objects.filter(ward__district=self).count()
        
        return {
            'wards': wards,
            'locations': locations
        }


class Ward(models.Model):
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
        District,
        on_delete=models.CASCADE,
        related_name='wards',
        db_index=True,
        help_text='District this ward belongs to'
    )
    
    # ========================================================================
    # WARD IDENTIFICATION
    # ========================================================================
    
    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='Code must contain only uppercase letters and numbers'
            )
        ],
        help_text='Ward code'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Ward name'
    )

    class Meta:
        db_table = 'wards'
        verbose_name = _('Ward')
        verbose_name_plural = _('Wards')
        ordering = ['district', 'name']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique code per district
            models.UniqueConstraint(
                fields=['district', 'code'],
                name='unique_district_ward_code'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for district queries
            models.Index(
                fields=['district'],
                name='idx_ward_district'
            ),
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
        return self.locations.all().order_by('name')

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
        return cls.objects.filter(
            district__province=province
        ).order_by('district', 'name')


class Location(models.Model):
    """
    Location model for specific addresses
    
    Features:
    - Ward relationship: Link to ward
    - Street address: Store street details
    - Coordinates: Store GPS coordinates
    - Location type: Classify location
    - Statistics: Track usage
    
    Location Types:
    - OFFICE: Office location
    - WAREHOUSE: Warehouse location
    - PICKUP: Pickup point
    - DELIVERY: Delivery point
    - BRANCH: Branch office
    - CUSTOM: Custom location
    
    Example:
        # Create location
        location = Location.objects.create(
            ward=ward,
            name='Main Office',
            address='123 Hang Trong St',
            location_type='OFFICE',
            latitude=21.0285,
            longitude=105.8542
        )
        
        # Get full address
        full_address = location.get_full_address()
        
        # Get distance to another location
        distance = location.get_distance_to(other_location)
    """

    LOCATION_TYPE_CHOICES = (
        ('OFFICE', _('Office - Office location')),
        ('WAREHOUSE', _('Warehouse - Warehouse location')),
        ('PICKUP', _('Pickup - Pickup point')),
        ('DELIVERY', _('Delivery - Delivery point')),
        ('BRANCH', _('Branch - Branch office')),
        ('CUSTOM', _('Custom - Custom location')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='locations',
        db_index=True,
        help_text='Ward this location is in'
    )
    
    # ========================================================================
    # LOCATION INFORMATION
    # ========================================================================
    
    name = models.CharField(
        max_length=200,
        help_text='Location name'
    )
    
    address = models.CharField(
        max_length=500,
        help_text='Street address'
    )
    
    location_type = models.CharField(
        max_length=30,
        choices=LOCATION_TYPE_CHOICES,
        default='CUSTOM',
        db_index=True,
        help_text='Type of location'
    )
    
    # ========================================================================
    # COORDINATES
    # ========================================================================
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Latitude coordinate'
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Longitude coordinate'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When location was created'
    )

    class Meta:
        db_table = 'locations'
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ['ward', 'name']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for ward queries
            models.Index(
                fields=['ward'],
                name='idx_location_ward'
            ),
            # Index for location type queries
            models.Index(
                fields=['location_type'],
                name='idx_location_type'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.ward.name})"

    # ========================================================================
    # ADDRESS METHODS
    # ========================================================================

    def get_full_address(self):
        """
        Get full address with hierarchy
        
        Returns:
            String
        
        Example:
            full = location.get_full_address()
            # Returns: "123 Hang Trong St, Hang Trong, Hoan Kiem, Hanoi"
        """
        parts = [
            self.address,
            self.ward.name,
            self.ward.district.name,
            self.ward.district.province.name
        ]
        return ', '.join(filter(None, parts))

    def get_short_address(self):
        """
        Get short address
        
        Returns:
            String
        
        Example:
            short = location.get_short_address()
            # Returns: "123 Hang Trong St, Hanoi"
        """
        return f"{self.address}, {self.ward.district.province.name}"

    def has_coordinates(self):
        """
        Check if location has coordinates
        
        Returns:
            Boolean
        
        Example:
            if location.has_coordinates():
                # Can calculate distance
        """
        return self.latitude is not None and self.longitude is not None

    def get_coordinates(self):
        """
        Get coordinates as tuple
        
        Returns:
            Tuple (latitude, longitude) or None
        
        Example:
            coords = location.get_coordinates()
        """
        if self.has_coordinates():
            return (float(self.latitude), float(self.longitude))
        return None

    def get_distance_to(self, other_location):
        """
        Calculate distance to another location (Haversine formula)
        
        Args:
            other_location: Location instance
        
        Returns:
            Float (distance in km) or None
        
        Example:
            distance = location.get_distance_to(other_location)
        """
        if not self.has_coordinates() or not other_location.has_coordinates():
            return None
        
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = self.latitude, self.longitude
        lat2, lon2 = other_location.latitude, other_location.longitude
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_by_province(cls, province):
        """
        Get all locations in province
        
        Args:
            province: Province instance
        
        Returns:
            QuerySet of Location objects
        
        Example:
            locations = Location.get_by_province(province)
        """
        return cls.objects.filter(
            ward__district__province=province
        ).order_by('ward__district', 'ward', 'name')

    @classmethod
    def get_by_district(cls, district):
        """
        Get all locations in district
        
        Args:
            district: District instance
        
        Returns:
            QuerySet of Location objects
        
        Example:
            locations = Location.get_by_district(district)
        """
        return cls.objects.filter(
            ward__district=district
        ).order_by('ward', 'name')

    @classmethod
    def get_by_type(cls, location_type):
        """
        Get locations by type
        
        Args:
            location_type: Location type
        
        Returns:
            QuerySet of Location objects
        
        Example:
            offices = Location.get_by_type('OFFICE')
        """
        return cls.objects.filter(
            location_type=location_type
        ).order_by('ward__district__province', 'name')

    @classmethod
    def search_locations(cls, query, province=None):
        """
        Search locations by name or address
        
        Args:
            query: Search query
            province: Optional province filter
        
        Returns:
            QuerySet of Location objects
        
        Example:
            results = Location.search_locations('Main Office', province)
        """
        from django.db.models import Q
        
        search_query = Q(name__icontains=query) | Q(address__icontains=query)
        
        if province:
            return cls.objects.filter(
                search_query,
                ward__district__province=province
            )
        
        return cls.objects.filter(search_query)