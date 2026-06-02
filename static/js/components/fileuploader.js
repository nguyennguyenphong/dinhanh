class CMSFileUploader {
    constructor(element) {
        if (!element) return;
        this.input = element;
        this.init();
    }

    init() {
        // Đọc cấu hình từ Data Attributes Python chuyển qua
        const isMultiple = this.input.dataset.multiple === 'true';
        const maxFiles = parseInt(this.input.dataset.maxFiles) || 1;
        const maxSize = this.input.dataset.maxSize || '10MB';
        
        let acceptedTypes = [];
        try {
            acceptedTypes = JSON.parse(this.input.dataset.acceptedTypes || '[]');
        } catch (e) {
            console.error("Error parsing accepted types:", e);
        }

        // 2. Khởi tạo FilePond Instance tiếng Anh chuẩn Production
        this.pond = FilePond.create(this.input, {
            storeAsFile: true,               // Đảm bảo file được đẩy thẳng vào thẻ form truyền thống lên Django
            allowMultiple: isMultiple,
            maxFiles: isMultiple ? maxFiles : 1,
            maxFileSize: maxSize,
            acceptedFileTypes: acceptedTypes.length > 0 ? acceptedTypes : null,
            
            // Nhãn hiển thị tiếng Anh (Clean & Clear)
            labelIdle: 'Drag & Drop your files or <span class="filepond--label-action">Browse</span>',
            labelFileTypeNotAllowed: 'File of invalid type',
            fileValidateTypeLabelExpectedTypes: 'Expects {allTypes}',
            labelMaxFileSizeExceeded: 'File is too large',
            labelMaxFileSize: 'Maximum file size is {maxFileSize}',
            
            // Cấu hình tính năng Xem trước (Preview)
            allowImagePreview: true,
            imagePreviewHeight: 170,        // Giới hạn chiều cao preview ảnh cho gọn giao diện CMS
            allowVideoPreview: true,        // Kích hoạt xem trước video thông qua plugin Media
            allowAudioPreview: true,
            
            // Xử lý sự kiện lỗi nếu có
            onwarning: (error) => {
                console.warn('FilePond Warning:', error);
            }
        });
    }

    destroy() {
        if (this.pond) this.pond.destroy();
    }
}

// 3. Tự động tìm kiếm và kích hoạt trên toàn hệ thống CMS
document.addEventListener("DOMContentLoaded", function () {
    // 1. Đăng ký các Plugins cần thiết với FilePond
    FilePond.registerPlugin(
        FilePondPluginFileValidateType,
        FilePondPluginFileValidateSize,
        FilePondPluginImagePreview,
        FilePondPluginMediaPreview
    );
    document.querySelectorAll('[data-cms-fileuploader]').forEach(el => new CMSFileUploader(el));
});