from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from core.middleware import get_current_user 

class BaseModel(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
        verbose_name=_("Updated by"),
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        
        if user and user.is_authenticated:
            if not self.pk:
                self.created_by = user
            self.updated_by = user
            
        super().save(*args, **kwargs)