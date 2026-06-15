1. Xóa tất cả file migration, giữ lại __init__.py
find . -path "*/migrations/*" -type f ! -name "__init__.py" -delete

Lệnh này sẽ xóa toàn bộ file trong các thư mục migrations, ngoại trừ __init__.py.

2. Xóa toàn bộ thư mục __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +