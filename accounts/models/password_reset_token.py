from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models.user_accounts import UserAccount

class PasswordResetToken(models.Model):
    """
    Password reset token model
    
    Features:
    - One-time use tokens
    - Expiration support
    - Track used tokens
    """
    
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text='User requesting password reset'
    )
    
    # Token
    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Reset token (one-time use)'
    )
    
    # Expiration
    expires_at = models.DateTimeField(
        help_text='Token expiration time'
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When token was used'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = _('Password Reset Token')
        verbose_name_plural = _('Password Reset Tokens')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    def is_expired(self):
        """
        Check if token has expired
        """
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_used(self):
        """
        Check if token has been used
        """
        return self.used_at is not None

    def mark_as_used(self):
        """
        Mark token as used (one-time use)
        """
        from django.utils import timezone
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])