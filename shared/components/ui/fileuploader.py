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
        allow_multiple=False,
        max_files=5,
        max_size="10MB",
        file_type="all",
        **attrs,
    ):
        mime_maps = {
            "image": ["image/*"], 
            "video": ["video/*"],
            "document": [
                "application/pdf", 
                "application/msword", 
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ],
            "all": []
        }

        # Nếu file_type không nằm trong map hoặc là 'all', để trống để cho phép mọi loại file
        accepted_mime = mime_maps.get(file_type, [])

        pond_attrs = {
            "data-cms-fileuploader": "",
            "data-name": name,
            "data-multiple": str(allow_multiple).lower(),
            "data-max-files": max_files,
            "data-max-size": max_size,
            # Nếu là 'all' hoặc danh sách rỗng, FilePond sẽ tự hiểu là không lọc
            "data-accepted-types": json.dumps(accepted_mime) if accepted_mime else "[]",
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