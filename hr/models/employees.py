# ============================================================================
# FILE: apps/employees/models.py
# Employees Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from hr.models.departments import Department
from branches.models.branches import Branch
from accounts.models.user_accounts import UserAccount  # Custom user model


class Employee(models.Model):
    """
    Employee model managing full staff profiles, payroll details, and operations compliance.
    
    Features:
    - Multi-tenancy: Securely partitioned via tenant_id
    - Account Mapping: Direct 1-to-1 linkage with system authentication (UserAccount)
    - Role & Position Classification: Covers drivers, dispatchers, and backend office roles
    - Driver Compliance: Keeps track of heavy commercial driving licenses and expiries
    - Financial & Insurance: Stores tax codes, insurance tokens, and bank routing assets
    - JSONB Support: Dynamic unstructured schema for emergency contact configurations
    
    Genders:
    - MALE: Male gender orientation
    - FEMALE: Female gender orientation
    - OTHER: Non-binary or custom gender orientation
    
    Positions:
    - DRIVER: Active fleet vehicle operator
    - ASSISTANT: Conductor / Trip crew assistant
    - CASHIER: Ticket counter or collection officer
    - DISPATCHER: Fleet operations router / Trip controller
    - ACCOUNTANT: Financial auditor
    - MANAGER: Corporate or branch leader
    - OTHER: Custom or miscellaneous corporate role
    
    Example:
        # Create a driver employee profile
        driver = Employee.objects.create(
            tenant_id=1,
            code='EMP-DRV-001',
            full_name='Nguyen Van A',
            position='DRIVER',
            hired_at='2026-01-15',
            license_number='290123456789',
            license_class='FC',
            license_expiry='2031-01-15',
            emergency_contact={"name": "Mary Doe", "relation": "Spouse", "phone": "0900000000"}
        )
    """

    GENDER_CHOICES = (
        ('MALE', _('Male')),
        ('FEMALE', _('Female')),
        ('OTHER', _('Other')),
    )

    POSITION_CHOICES = (
        ('DRIVER', _('Driver - Fleet vehicle operator')),
        ('ASSISTANT', _('Assistant - Trip conductor crew')),
        ('CASHIER', _('Cashier - Ticket collection staff')),
        ('DISPATCHER', _('Dispatcher - Trip operations coordinator')),
        ('ACCOUNTANT', _('Accountant - Financial staff')),
        ('MANAGER', _('Manager - General leadership line')),
        ('OTHER', _('Other - Custom staff classification')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name='employees',
        db_index=True,
        help_text='Tenant owner of this employee record'
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL
        related_name='employees',
        null=True,
        blank=True,
        db_index=True,
        help_text='Corporate organizational department division mapping'
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL
        related_name='employees',
        null=True,
        blank=True,
        db_index=True,
        help_text='Physical home branch or hub where staff reports to work'
    )
    
    user_account = models.OneToOneField(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL / UNIQUE combined
        related_name='employee_profile',
        null=True,
        blank=True,
        help_text='Associated system user credentials for dashboard and portal login permissions'
    )
    
    # ========================================================================
    # CORE PROFILE INFORMATION
    # ========================================================================
    
    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-_]+$',
                message='Code must contain only uppercase letters, numbers, hyphens, and underscores'
            )
        ],
        help_text='Unique business identifier system code (e.g., EMP-2026-09)'
    )
    
    full_name = models.CharField(
        max_length=255,
        help_text='Official full legal name of the employee'
    )
    
    national_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='National identity card or citizenship passport index (e.g., CCCD)'
    )
    
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r'^\+?[0-9\s.\-]+$', message='Invalid phone format')],
        help_text='Primary mobile or telecommunication entry node'
    )
    
    email = models.CharField(
        max_length=244,  # Fits up to standard RFC limits safely
        null=True,
        blank=True,
        validators=[EmailValidator()],
        help_text='Corporate or personal communication contact mailbox address'
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Official birth record calendar date'
    )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        help_text='Biological or legal identity gender profile token'
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        help_text='Current residential or permanent accommodation address'
    )
    
    position = models.CharField(
        max_length=100,
        choices=POSITION_CHOICES,
        db_index=True,
        help_text='Active job role designation within operational flows'
    )
    
    # ========================================================================
    # LIFECYCLE TIMESTAMPS & CONTRACT FLOWS
    # ========================================================================
    
    hired_at = models.DateField(
        help_text='Calendar date when employment officially commenced'
    )
    
    terminated_at = models.DateField(
        null=True,
        blank=True,
        help_text='Calendar date when employment contract was formally ended'
    )
    
    termination_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Internal exit log detailing background factors for termination'
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Designates whether this employee is currently working and on the active payroll'
    )
    
    # ========================================================================
    # DRIVER-SPECIFIC COMPLIANCE BLUEPRINT
    # ========================================================================
    
    license_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Commercial vehicle driving license identifier token number'
    )
    
    license_class = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='Driving license category tier classification (e.g., B2, C, D, E, FC)'
    )
    
    license_expiry = models.DateField(
        null=True,
        blank=True,
        help_text='Driving license legal validation expiry date threshold'
    )
    
    # ========================================================================
    # PAYROLL, INSURANCE & TAXATION PROFILE
    # ========================================================================
    
    social_insurance_no = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='State-managed social insurance registry profile book identification code'
    )
    
    health_insurance_no = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='National health care safety insurance policy tracking index'
    )
    
    tax_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Personal income tax individual registration index number (PIT)'
    )
    
    bank_account = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text='Bank routing ledger account identity number for salary wire disbursements'
    )
    
    bank_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Official institutional commercial bank corporate name'
    )
    
    # Native PostgreSQL JSONB architecture integration
    emergency_contact = models.JSONField(
        default=dict,
        help_text='Complex data object capturing name, kinship relation, phone node array for accidents'
    )
    
    # ========================================================================
    # AUDIT LOGS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this personnel file was first created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when this personnel profile was last modified'
    )

    class Meta:
        db_table = 'employees'
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['tenant', '-is_active', 'full_name']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique employee code per tenant (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_tenant_employee_code'
            ),
            # Direct database-level CHECK constraint for gender structure safety
            models.CheckConstraint(
                condition=models.Q(
                    gender__in=[
                        'MALE',
                        'FEMALE',
                        'OTHER'
                    ]
                ),
                name='chk_employee_gender'
            )
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for lightning-fast lookups on personnel catalogs by branch operational status
            models.Index(
                fields=['branch', 'is_active', 'position'],
                name='idx_emp_branch_dispatch'
            ),
            # Chronological optimization for compliance alert processing tasks (e.g., license expiries)
            models.Index(
                fields=['license_expiry'],
                name='idx_emp_license_compliance'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.code}] {self.full_name} - {self.get_position_display()}"

    # ========================================================================
    # BUSINESS LOGIC & COMPLIANCE VERIFICATION METHODS
    # ========================================================================

    def is_driver(self):
        """
        Verify if this personnel file belongs to an active fleet driver.
        
        Returns:
            Boolean
        """
        return self.position == 'DRIVER'

    def has_expired_license(self):
        """
        Verify if the commercial operator license has passed validation safety dates.
        
        Returns:
            Boolean
        """
        if not self.is_driver() or not self.license_expiry:
            return False
            
        from django.utils import timezone
        return self.license_expiry < timezone.localdate()

    def terminate_employment(self, reason, exit_date=None):
        """
        Safely execute termination flow, decommission auth access blocks, and close out payroll lines.
        
        Args:
            reason: String
            exit_date: Date object (defaults to current date)
        """
        from django.utils import timezone
        
        self.is_active = False
        self.terminated_at = exit_date or timezone.localdate()
        self.termination_reason = reason
        self.save(update_fields=['is_active', 'terminated_at', 'termination_reason', 'updated_at'])
        
        # Security protocol: Unlink or deactivate auth user immediately to revoke portal permissions
        if self.user_account:
            self.user_account.is_active = False
            self.user_account.save(update_fields=['is_active', 'updated_at'])

    # ========================================================================
    # CLASSMETHODS / ORGANIZATIONAL ROSTER QUERIES
    # ========================================================================

    @classmethod
    def get_available_drivers_by_branch(cls, branch_id):
        """
        Fetch active drivers matching a localized branch depot who are ready for dispatching.
        
        Args:
            branch_id: Integer
            
        Returns:
            QuerySet of Employee objects
        """
        return cls.objects.filter(
            branch_id=branch_id,
            position='DRIVER',
            is_active=True
        ).order_by('full_name')