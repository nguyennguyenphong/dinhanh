class FileUploader {
    constructor(element) {
        if (!element) return;
        this.input = element;
        this.init();
    }

    init() {
        const isMultiple = this.input.dataset.multiple === 'true';
        const maxFiles = parseInt(this.input.dataset.maxFiles) || 1;
        const maxSize = this.input.dataset.maxSize || '10MB';

        let acceptedTypes = [];
        try {
            acceptedTypes = JSON.parse(this.input.dataset.acceptedTypes || '[]');
        } catch (e) {
            console.error("Error parsing accepted types:", e);
        }

        this.pond = FilePond.create(this.input, {
            storeAsFile: true,

            allowMultiple: isMultiple,
            maxFiles: isMultiple ? maxFiles : 1,

            maxFileSize: maxSize,

            acceptedFileTypes:
                acceptedTypes.length
                    ? acceptedTypes
                    : undefined,

            allowImagePreview: true,

            labelIdle:
                'Drag & Drop files or <span class="filepond--label-action">Browse</span>',

            labelFileTypeNotAllowed:
                'Invalid file type',

            fileValidateTypeLabelExpectedTypes:
                'Allowed: {allTypes}',

            labelMaxFileSizeExceeded:
                'File too large',

            labelMaxFileSize:
                'Maximum size: {maxFileSize}',

            onwarning: error =>
                console.warn(error),

            onerror: error =>
                console.error(error),

            fileValidateTypeDetectType: (source, type) => new Promise((resolve, reject) => {
                if (type.startsWith('image/')) {
                    resolve(type);
                } else {
                    resolve('image/jpeg');
                }
            }),

            allowFileTypeValidation: true,
        });
    }

    destroy() {
        if (this.pond) this.pond.destroy();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    FilePond.registerPlugin(
        FilePondPluginFileValidateType,
        FilePondPluginFileValidateSize,
        FilePondPluginImagePreview,
        FilePondPluginMediaPreview
    );
    document.querySelectorAll('[data-cms-fileuploader]').forEach(el => new FileUploader(el));
});