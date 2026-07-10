from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class OTPCode(BaseModel):
    """
    OTP code model for registration and password resets.
    """

    id = models.AutoField(primary_key=True)
    email = models.EmailField(_("Email Address"), db_index=True)
    code = models.CharField(_("OTP Code"), max_length=6)
    purpose = models.CharField(
        _("Purpose"),
        max_length=50,
        choices=[("REGISTER", "Register"), ("PASSWORD_RESET", "Password Reset")],
    )
    expires_at = models.DateTimeField(_("Expires At"))
    is_used = models.BooleanField(_("Is Used"), default=False)

    class Meta:
        db_table = "otp_codes"
        verbose_name = _("OTP Code")
        verbose_name_plural = _("OTP Codes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.code} ({self.purpose})"
