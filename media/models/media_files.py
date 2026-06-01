# ============================================================================
# FILE: apps/media/models.py
# Media File Models with Multi-Storage Support
# ============================================================================

import mimetypes
import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tenants.models.tenants import Tenant


class MediaFile(models.Model):
    """
    Media file model for managing uploaded files

    Features:
    - Multi-tenant support: Each tenant has own media files
    - Multi-storage support: Local, S3, GCS, Azure
    - UUID tracking: Unique identifier for each file
    - Image dimensions: Store width/height for images
    - Public/private: Control file access
    - Entity linking: Link files to entities (vehicles, employees, etc.)
    - Upload tracking: Track who uploaded and when
    - URL generation: Generate download URLs
    - Cleanup: Automatic cleanup of deleted files

    Storage Options:
    - local: Local filesystem storage
    - s3: Amazon S3
    - gcs: Google Cloud Storage
    - azure: Azure Blob Storage

    Entity Types:
    - vehicles: Vehicle photos/documents
    - employees: Employee photos/documents
    - bookings: Booking attachments
    - trips: Trip documents
    - invoices: Invoice files
    - receipts: Receipt files
    - custom: Custom entity types

    File Handling:
    - Original name: Preserved for display
    - Stored name: Sanitized name for storage
    - File path: Full path in storage
    - URL: Generated URL for download/display

    Example:
        # Upload file
        media = MediaFile.create_from_upload(
            tenant=tenant,
            file=uploaded_file,
            uploaded_by=user,
            entity_type='vehicles',
            entity_id=vehicle.id,
            is_public=False
        )

        # Get download URL
        url = media.get_url()

        # Get thumbnail
        thumb_url = media.get_thumbnail_url(size='small')

        # Delete file
        media.delete()
    """

    STORAGE_CHOICES = (
        ("local", _("Local - Local filesystem")),
        ("s3", _("S3 - Amazon S3")),
        ("gcs", _("GCS - Google Cloud Storage")),
        ("azure", _("Azure - Azure Blob Storage")),
    )

    ENTITY_TYPE_CHOICES = (
        ("vehicles", _("Vehicles - Vehicle photos/documents")),
        ("employees", _("Employees - Employee photos/documents")),
        ("bookings", _("Bookings - Booking attachments")),
        ("trips", _("Trips - Trip documents")),
        ("invoices", _("Invoices - Invoice files")),
        ("receipts", _("Receipts - Receipt files")),
        ("avatars", _("Avatars - User profile pictures")),
        ("documents", _("Documents - General documents")),
        ("custom", _("Custom - Custom entity types")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="media_files",
        db_index=True,
        help_text="Tenant that owns this media file",
    )

    # ========================================================================
    # FILE IDENTIFICATION
    # ========================================================================

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        help_text="Unique identifier for this file",
    )
    original_name = models.CharField(
        max_length=500, help_text="Original filename as uploaded"
    )
    stored_name = models.CharField(
        max_length=500, help_text="Sanitized filename for storage"
    )

    # ========================================================================
    # STORAGE INFORMATION
    # ========================================================================

    storage = models.CharField(
        max_length=30,
        choices=STORAGE_CHOICES,
        default="local",
        help_text="Storage backend used",
    )
    bucket = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Bucket name (for cloud storage)",
    )
    file_path = models.CharField(
        max_length=1000, help_text="Full path to file in storage"
    )
    url = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="Generated URL for file access",
    )

    # ========================================================================
    # FILE METADATA
    # ========================================================================

    mime_type = models.CharField(
        max_length=100, null=True, blank=True, help_text="MIME type (e.g., image/jpeg)"
    )
    size_bytes = models.BigIntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )

    # ========================================================================
    # IMAGE METADATA
    # ========================================================================

    width = models.IntegerField(
        null=True, blank=True, help_text="Image width in pixels (for images)"
    )
    height = models.IntegerField(
        null=True, blank=True, help_text="Image height in pixels (for images)"
    )

    # ========================================================================
    # ACCESS CONTROL
    # ========================================================================

    is_public = models.BooleanField(
        default=False, db_index=True, help_text="File is publicly accessible"
    )

    # ========================================================================
    # UPLOAD TRACKING
    # ========================================================================

    uploaded_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_media_files",
        help_text="User who uploaded this file",
    )

    # ========================================================================
    # ENTITY LINKING
    # ========================================================================

    entity_type = models.CharField(
        max_length=60,
        choices=ENTITY_TYPE_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text="Type of entity this file is linked to",
    )
    entity_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="ID of entity this file is linked to",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this file was uploaded"
    )

    class Meta:
        db_table = "media_files"
        verbose_name = _("Media File")
        verbose_name_plural = _("Media Files")
        ordering = ["-created_at"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding files by entity
            models.Index(fields=["entity_type", "entity_id"], name="idx_media_entity"),
            # Index for finding files by uploader
            models.Index(fields=["uploaded_by"], name="idx_media_uploader"),
            # Index for finding public files
            models.Index(fields=["is_public"], name="idx_media_public"),
            # Index for tenant queries
            models.Index(
                fields=["tenant", "created_at"], name="idx_media_tenant_created"
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.original_name} ({self.size_bytes} bytes)"

    def clean(self):
        """
        Validate media file
        """
        # Validate entity type and ID
        if (self.entity_type and not self.entity_id) or (
            not self.entity_type and self.entity_id
        ):
            raise ValidationError(
                "Both entity_type and entity_id must be provided together"
            )

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # FILE PROPERTIES
    # ========================================================================

    def is_image(self):
        """
        Check if file is an image

        Returns:
            Boolean
        """
        if not self.mime_type:
            return False
        return self.mime_type.startswith("image/")

    def is_video(self):
        """
        Check if file is a video

        Returns:
            Boolean
        """
        if not self.mime_type:
            return False
        return self.mime_type.startswith("video/")

    def is_document(self):
        """
        Check if file is a document

        Returns:
            Boolean
        """
        if not self.mime_type:
            return False

        document_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]

        return self.mime_type in document_types

    def get_file_extension(self):
        """
        Get file extension

        Returns:
            String (e.g., 'jpg', 'pdf')
        """
        _, ext = os.path.splitext(self.original_name)
        return ext.lstrip(".").lower()

    def get_file_size_display(self):
        """
        Get human-readable file size

        Returns:
            String (e.g., '2.5 MB')
        """
        size = self.size_bytes

        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024

        return f"{size:.1f} TB"

    # ========================================================================
    # URL METHODS
    # ========================================================================

    def get_url(self, expires_in=None):
        """
        Get file download URL

        Args:
            expires_in: Expiration time in seconds (for signed URLs)

        Returns:
            String URL

        Example:
            url = media.get_url()
            # Returns: 'https://storage.example.com/media/...'
        """
        if self.url:
            return self.url

        # Generate URL based on storage backend
        if self.storage == "local":
            return f"/media/{self.file_path}"

        elif self.storage == "s3":
            # Generate S3 URL
            from django.conf import settings

            return f"https://{self.bucket}.s3.amazonaws.com/{self.file_path}"

        elif self.storage == "gcs":
            # Generate GCS URL
            return f"https://storage.googleapis.com/{self.bucket}/{self.file_path}"

        elif self.storage == "azure":
            # Generate Azure URL
            return f"https://{self.bucket}.blob.core.windows.net/{self.file_path}"

        return None

    def get_thumbnail_url(self, size="small", expires_in=None):
        """
        Get thumbnail URL

        Args:
            size: Thumbnail size (small, medium, large)
            expires_in: Expiration time in seconds

        Returns:
            String URL or None

        Example:
            thumb = media.get_thumbnail_url(size='small')
        """
        if not self.is_image():
            return None

        # Generate thumbnail path
        base_path, ext = os.path.splitext(self.file_path)
        thumb_path = f"{base_path}_thumb_{size}{ext}"

        if self.storage == "local":
            return f"/media/{thumb_path}"

        elif self.storage == "s3":
            return f"https://{self.bucket}.s3.amazonaws.com/{thumb_path}"

        elif self.storage == "gcs":
            return f"https://storage.googleapis.com/{self.bucket}/{thumb_path}"

        elif self.storage == "azure":
            return f"https://{self.bucket}.blob.core.windows.net/{thumb_path}"

        return None

    # ========================================================================
    # CREATION METHODS
    # ========================================================================

    @classmethod
    def create_from_upload(
        cls,
        tenant,
        file,
        uploaded_by=None,
        entity_type=None,
        entity_id=None,
        is_public=False,
        storage="local",
    ):
        """
        Create media file from uploaded file

        Args:
            tenant: Tenant instance
            file: Django UploadedFile
            uploaded_by: UserAccount instance
            entity_type: Entity type
            entity_id: Entity ID
            is_public: Public access flag
            storage: Storage backend

        Returns:
            MediaFile instance

        Example:
            media = MediaFile.create_from_upload(
                tenant=tenant,
                file=request.FILES['image'],
                uploaded_by=user,
                entity_type='vehicles',
                entity_id=vehicle.id
            )
        """
        # Generate stored name
        original_name = file.name
        ext = os.path.splitext(original_name)[1]
        stored_name = f"{uuid.uuid4()}{ext}"

        # Generate file path
        date_path = timezone.now().strftime("%Y/%m/%d")
        file_path = f"uploads/{tenant.code}/{date_path}/{stored_name}"

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(original_name)

        # Create media file record
        media = cls.objects.create(
            tenant=tenant,
            original_name=original_name,
            stored_name=stored_name,
            storage=storage,
            file_path=file_path,
            mime_type=mime_type,
            size_bytes=file.size,
            uploaded_by=uploaded_by,
            entity_type=entity_type,
            entity_id=entity_id,
            is_public=is_public,
        )

        # Save file to storage
        media._save_to_storage(file)

        # Extract image dimensions if image
        if media.is_image():
            media._extract_image_dimensions()

        return media

    def _save_to_storage(self, file):
        """
        Save file to storage backend

        Args:
            file: Django UploadedFile
        """
        if self.storage == "local":
            self._save_to_local(file)
        elif self.storage == "s3":
            self._save_to_s3(file)
        elif self.storage == "gcs":
            self._save_to_gcs(file)
        elif self.storage == "azure":
            self._save_to_azure(file)

    def _save_to_local(self, file):
        """Save to local storage"""
        from django.conf import settings

        # Create directory
        full_path = os.path.join(settings.MEDIA_ROOT, self.file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save file
        with open(full_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

    def _save_to_s3(self, file):
        """Save to S3"""
        import boto3
        from django.conf import settings

        s3 = boto3.client("s3")
        s3.upload_fileobj(
            file, self.bucket or settings.AWS_STORAGE_BUCKET_NAME, self.file_path
        )

    def _save_to_gcs(self, file):
        """Save to Google Cloud Storage"""
        from google.cloud import storage as gcs_storage

        client = gcs_storage.Client()
        bucket = client.bucket(self.bucket)
        blob = bucket.blob(self.file_path)
        blob.upload_from_file(file)

    def _save_to_azure(self, file):
        """Save to Azure Blob Storage"""
        from azure.storage.blob import BlobServiceClient
        from django.conf import settings

        service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        blob_client = service_client.get_blob_client(
            container=self.bucket, blob=self.file_path
        )
        blob_client.upload_blob(file, overwrite=True)

    def _extract_image_dimensions(self):
        """Extract image dimensions"""
        try:
            import io

            from PIL import Image

            if self.storage == "local":
                from django.conf import settings

                full_path = os.path.join(settings.MEDIA_ROOT, self.file_path)
                img = Image.open(full_path)
            else:
                # Download from cloud storage
                url = self.get_url()
                import requests

                response = requests.get(url)
                img = Image.open(io.BytesIO(response.content))

            self.width, self.height = img.size
            self.save(update_fields=["width", "height"])
        except Exception:
            pass

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_by_entity(cls, entity_type, entity_id):
        """
        Get all files for an entity

        Args:
            entity_type: Entity type
            entity_id: Entity ID

        Returns:
            QuerySet of MediaFile objects

        Example:
            files = MediaFile.get_by_entity('vehicles', vehicle.id)
        """
        return cls.objects.filter(
            entity_type=entity_type, entity_id=entity_id
        ).order_by("-created_at")

    @classmethod
    def get_by_uploader(cls, tenant, user):
        """
        Get all files uploaded by a user

        Args:
            tenant: Tenant instance
            user: UserAccount instance

        Returns:
            QuerySet of MediaFile objects
        """
        return cls.objects.filter(tenant=tenant, uploaded_by=user).order_by(
            "-created_at"
        )

    @classmethod
    def get_public_files(cls, tenant):
        """
        Get all public files

        Args:
            tenant: Tenant instance

        Returns:
            QuerySet of MediaFile objects
        """
        return cls.objects.filter(tenant=tenant, is_public=True).order_by("-created_at")

    # ========================================================================
    # CLEANUP METHODS
    # ========================================================================

    def delete_file(self):
        """
        Delete file from storage

        Example:
            media.delete_file()
        """
        if self.storage == "local":
            self._delete_from_local()
        elif self.storage == "s3":
            self._delete_from_s3()
        elif self.storage == "gcs":
            self._delete_from_gcs()
        elif self.storage == "azure":
            self._delete_from_azure()

    def _delete_from_local(self):
        """Delete from local storage"""
        from django.conf import settings

        full_path = os.path.join(settings.MEDIA_ROOT, self.file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    def _delete_from_s3(self):
        """Delete from S3"""
        import boto3
        from django.conf import settings

        s3 = boto3.client("s3")
        s3.delete_object(
            Bucket=self.bucket or settings.AWS_STORAGE_BUCKET_NAME, Key=self.file_path
        )

    def _delete_from_gcs(self):
        """Delete from GCS"""
        from google.cloud import storage as gcs_storage

        client = gcs_storage.Client()
        bucket = client.bucket(self.bucket)
        blob = bucket.blob(self.file_path)
        blob.delete()

    def _delete_from_azure(self):
        """Delete from Azure"""
        from azure.storage.blob import BlobServiceClient
        from django.conf import settings

        service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        blob_client = service_client.get_blob_client(
            container=self.bucket, blob=self.file_path
        )
        blob_client.delete_blob()

    def delete(self, *args, **kwargs):
        """Override delete to cleanup file"""
        self.delete_file()
        super().delete(*args, **kwargs)
