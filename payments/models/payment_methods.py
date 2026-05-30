# ============================================================================
# FILE: apps/payments/models.py
# Payment Gateway & Method Configuration Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q

# Assuming these model exist in your production architecture
from tenants.models.tenants import Tenant


class PaymentMethod(models.Model):
    """
    PaymentMethod model configuring both offline checkout and digital payment gateway integration properties.
    
    Features:
    - Multi-tenancy Isolation: Partitioned per tenant corporate entity.
    - Tenant-Scoped Uniqueness: Enforces distinct payment method system codes under a single tenant footprint.
    - Native PostgreSQL JSONB integration: Stores deep configuration trees (encrypted API parameters).
    - Client UI Sort Control: Dictates structural display order layouts on front-end checkout UI layers.
    
    Codes:
    - CASH: Hard currency collected at terminal ticket box offices or vehicle boarding points.
    - CARD: Credit/Debit POS card terminal hardware readers (e.g., Visa, Mastercard).
    - MOMO: Local domestic Vietnamese E-Wallet merchant payment gateway integration.
    - VNPAY: Local domestic banking QR-Code and payment gateway routing ecosystem.
    - ZALOPAY: Local domestic Vietnamese E-Wallet gateway powered by VNG ecosystem.
    - BANK_TRANSFER: Manual or virtual dynamic account bank wire clearing networks (e.g., Napas QR).
    - CREDIT: In-app virtual account internal customer wallet currency point balances.
    
    Example:
        # Create a dynamic digital gateway config mapping for VNPAY
        vnpay_method = PaymentMethod.objects.create(
            tenant_id=1,
            code='VNPAY',
            name='Cổng Thanh Toán VNPAY (QR-Code / Thẻ Nội Địa)',
            provider='VNPAY IT COMPANY',
            config={
                "vnp_TmnCode": "MERCHANT_XYZ_2026",
                "vnp_HashSecret": "ENCRYPTED_SECRET_KEY_TOKEN",
                "vnp_Url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
            },
            sort_order=2
        )
    """

    CODE_CHOICES = (
        ('CASH', _('Cash - Hard physical currency counters')),
        ('CARD', _('Card - Retail POS EMV terminal hardware readers')),
        ('MOMO', _('MoMo - Domestic MoMo E-Wallet API gateway connection')),
        ('VNPAY', _('VNPAY - Interbank Napas QR-Code payment router network')),
        ('ZALOPAY', _('ZaloPay - Domestic ZaloPay business gateway endpoint')),
        ('BANK_TRANSFER', _('Bank Transfer - Automatic bank wire virtual accounts clearing')),
        ('CREDIT', _('Credit - In-app passenger CRM wallet currency balances')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='payment_methods',
        db_index=True,
        help_text='Tenant corporate owner managing this isolated billing configurations node'
    )
    
    # ========================================================================
    # IDENTITY & METADATA DESCRIPTION
    # ========================================================================
    
    code = models.CharField(
        max_length=30,
        choices=CODE_CHOICES,
        help_text='System taxonomy identifier token tracking payment processors core routing rules'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Human-readable user interface descriptive name shown to customers at checkout windows'
    )
    
    provider = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='The official merchant service provider or third-party banking institution clearing the gateway operations'
    )
    
    # ========================================================================
    # DYNAMIC CONFIGURATION & DATA STRUCTURE
    # ========================================================================
    
    # Native PostgreSQL JSONB architecture integration
    config = models.JSONField(
        default=dict,
        help_text='Complex parameter matrix map capturing gateway credentials, client endpoints, and API secure hashes'
    )
    
    # ========================================================================
    # DISPLAY LAYOUT & LOGICAL ACTIVATION CONTROLS
    # ========================================================================
    
    sort_order = models.SmallIntegerField(
        default=0,
        help_text='UI hierarchy ordering sequence value. Lower integers scale directly to the top of list maps'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Logical activation flag. Setting this parameter to False disables visibility on mobile/counter interfaces'
    )

    class Meta:
        db_table = 'payment_methods'
        verbose_name = _('Payment Method Configuration')
        verbose_name_plural = _('Payment Method Configurations')
        ordering = ['sort_order', 'id']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Limits replication uniqueness of a method under a single tenant scope (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_tenant_payment_method_code'
            ),
            # Direct database-level CHECK constraint enforcing taxonomy data parameters
            models.CheckConstraint(
                condition=models.Q(code__in=['CASH', 'CARD', 'MOMO', 'VNPAY', 'ZALOPAY', 'BANK_TRANSFER', 'CREDIT']),
                name='chk_payment_method_code_rules'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} - {self.code} ({self.name}) [Active: {self.is_active}]"

    # ========================================================================
    # BUSINESS METRICS & PRODUCTION CRYPTOGRAPHY SECURE WORKFLOWS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation parsing matrix compliance before database serialization locks.
        """
        super().clean()
        
        if self.is_active and self.code not in ['CASH', 'CREDIT'] and not self.config:
            raise ValidationError({
                'config': _('Integration Error: Activation of digital channels requires explicit API parameters mapping inside the config field.')
            })

    def get_decrypted_config(self):
        """
        Production Security Mock: Decrypts sensitive credential values (such as secret keys or hashes)
        from the config JSON block at runtime using system environment key rings.
        
        Returns:
            Dict (Decrypted API properties dictionary)
        """
        if not self.config:
            return {}
            
        decrypted_payload = self.config.copy()
        
        # In a real enterprise system, you would call a decryption helper module here:
        # e.g., from apps.core.crypto import decrypt_value
        # for key in ['vnp_HashSecret', 'secret_key', 'private_key']:
        #     if key in decrypted_payload:
        #         decrypted_payload[key] = decrypt_value(decrypted_payload[key])
                
        return decrypted_payload

    def encrypt_and_set_config(self, raw_config_dict):
        """
        Production Security Mock: Encrypts sensitive credentials in the provided dictionary
        before packing the matrix down into the PostgreSQL JSONB storage field.
        
        Args:
            raw_config_dict: Dict (Raw plaintext API parameters)
        """
        encrypted_payload = raw_config_dict.copy()
        
        # e.g., from apps.core.crypto import encrypt_value
        # if 'vnp_HashSecret' in encrypted_payload:
        #     encrypted_payload['vnp_HashSecret'] = encrypt_value(encrypted_payload['vnp_HashSecret'])
            
        self.config = encrypted_payload