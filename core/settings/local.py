import environ

from core.settings.base import *  # noqa: F403, F401

env = environ.Env()

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = [
    "*"
]  # env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "127.0.0.1:8000"])

LOGIN_URL = "http://127.0.0.1:8000/accounts/login/"

INSTALLED_APPS += [
    "django_extensions",
    "django_browser_reload",
]

MIDDLEWARE.insert(1, "django_browser_reload.middleware.BrowserReloadMiddleware")

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME", default="dinhanh_db"),
        "USER": env("DATABASE_USER", default="dinhanh_user"),
        "PASSWORD": env("DATABASE_PASSWORD", default="T+75yTa_Z(wj"),
        "HOST": env("DATABASE_HOST", default="localhost"),
        "PORT": env("DATABASE_PORT", default="5432"),
        # Performance settings
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "connect_timeout": 10,
        },
        # Connection pooling
        "ATOMIC_REQUESTS": False,
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

#
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True


#

COMPRESS_ROOT = BASE_DIR / "static"

COMPRESS_ENABLED = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# Toolbar configuration for CKEditor 5
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
            "imageUpload",
        ],
        "toolbar": [
            "heading",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "alignment",
            "outdent",
            "indent",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "insertTable",
            "mediaEmbed",
            "codeBlock",
            "htmlEmbed",
            "|",
            "imageUpload",
            "|",
            "sourceEditing",
            "|",
            "undo",
            "redo",
        ],
        "upload_url": "ck_editor_5_upload_file",
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "|",
                "resizeImage",
            ],
            "styles": [
                "alignLeft",
                "alignCenter",
                "alignRight",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ]
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
                {
                    "model": "heading4",
                    "view": "h4",
                    "title": "Heading 4",
                    "class": "ck-heading_heading4",
                },
            ]
        },
        "htmlSupport": {
            "allow": [
                {"name": "/.*/", "attributes": True, "classes": True, "styles": True}
            ]
        },
    },
}
