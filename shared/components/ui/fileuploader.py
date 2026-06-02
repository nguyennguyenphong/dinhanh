import json
from django_components import Component, register


@register("fileuploader")
class FileUploader(Component):
    template_file = "components/ui/fileuploader.html"

    def get_context_data(
        self,
        label=None,
        name="",
        required=False,
        disabled=False,
        help_text=None,
        error=None,
        wrapper_class="",
        # --- Cấu hình riêng cho FilePond ---
        allow_multiple=False,       # Cho phép up nhiều file cùng lúc: True/False
        max_files=5,                # Số lượng file tối đa nếu chọn nhiều
        max_size="10MB",            # Dung lượng tối đa của 1 file (Ví dụ: 5MB, 50MB, 1GB)
        file_type="all",            # Các nhóm phím tắt: 'image', 'video', 'document', hoặc 'all'
        **attrs,
    ):
        # Bản đồ định nghĩa MIME types chuẩn Production
        mime_maps = {
            "image": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"],
            "video": ["video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo"],
            "document": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
            "all": [] # Sẽ xử lý chấp nhận tất cả ở JS nếu để trống
        }

        accepted_mime = mime_maps.get(file_type, [])

        pond_attrs = {
            "data-cms-fileuploader": "",
            "data-name": name,
            "data-multiple": str(allow_multiple).lower(),
            "data-max-files": max_files,
            "data-max-size": max_size,
            "data-accepted-types": json.dumps(accepted_mime),
        }
        attrs.update(pond_attrs)

        return {
            "label": label,
            "name": name,
            "id": attrs.get("id") or name,
            "required": required,
            "disabled": disabled,
            "help_text": help_text,
            "error": error,
            "wrapper_class": wrapper_class,
            "attrs": attrs,
        }