import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from PIL import Image


class FileStorageService:
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    # Path: tenants/media/logo/
    UPLOAD_DIR = "logo"

    # Đường dẫn lưu file: tenants/media/logo/
    UPLOAD_DIR = "logo"

    @staticmethod
    def save_tenant_logo(file_obj) -> str:
        """
        Validate and save file to tenants/media/logo/ folder.
        Return file url: /media/logo/uuid.ext
        """
        if not file_obj:
            raise ValidationError("Không có tệp nào được gửi.")

        if file_obj.size > FileStorageService.MAX_FILE_SIZE:
            raise ValidationError(
                f"Kích thước tệp vượt quá {FileStorageService.MAX_FILE_SIZE / (1024*1024):.0f}MB."
            )

        file_name = file_obj.name.lower()
        ext = os.path.splitext(file_name)[1].lstrip(".")

        if ext not in FileStorageService.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Định dạng tệp không được hỗ trợ. Chỉ chấp nhận: {', '.join(FileStorageService.ALLOWED_EXTENSIONS)}"
            )

        # 4. Validate image integrity
        try:
            img = Image.open(file_obj)
            img.verify()
            file_obj.seek(0)
        except Exception:
            raise ValidationError("Tệp ảnh không hợp lệ hoặc bị hỏng.")

        unique_filename = f"{FileStorageService.UPLOAD_DIR}/{uuid.uuid4()}.{ext}"

        file_path = default_storage.save(unique_filename, file_obj)

        # 7. Return URL
        # URL sẽ là: /media/logo/uuid.ext
        file_url = default_storage.url(file_path)
        return file_url

    @staticmethod
    def delete_logo(file_url: str):
        """
        Delete logo file by URL
        """
        if not file_url:
            return

        try:
            path_to_delete = file_url.replace(settings.MEDIA_URL, "", 1)
            if default_storage.exists(path_to_delete):
                default_storage.delete(path_to_delete)
        except Exception as e:
            print(f"Lỗi khi xóa logo cũ: {e}")

    @staticmethod
    def get_logo_dir() -> Path:
        """Get the full path to logo directory"""
        return Path(settings.MEDIA_ROOT) / FileStorageService.UPLOAD_DIR

    @staticmethod
    def delete_tenant_logo(logo_url: str) -> bool:
        """
        Delete logo file by URL
        Example: /media/logo/uuid.ext -> logo/uuid.ext
        """
        if not logo_url:
            return False

        try:
            # Extract file path from URL
            if logo_url.startswith("/media/"):
                file_path = logo_url.replace("/media/", "")
            else:
                file_path = logo_url

            default_storage.delete(file_path)
            return True
        except Exception as e:
            print(f"Error deleting logo: {str(e)}")
            return False

    @staticmethod
    def get_absolute_logo_path(logo_url: str) -> Path | None:
        """Get absolute file path from URL"""
        if not logo_url:
            return None

        if logo_url.startswith("/media/"):
            file_path = logo_url.replace("/media/", "")
        else:
            file_path = logo_url

        full_path = Path(settings.MEDIA_ROOT) / file_path
        return full_path if full_path.exists() else None
