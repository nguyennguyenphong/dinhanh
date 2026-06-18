```python
markdown_content = """# Django Cleanup Commands (Linux/macOS & Windows)

This document provides commands to clean up Django migration files and `__pycache__` directories for both Unix-like systems (Linux/macOS) and Windows (Command Prompt & PowerShell).

---

## 1. Delete all migration files, keeping `__init__.py` / Xóa tất cả file migration, giữ lại `__init__.py`

This command deletes all files inside `migrations` directories across your project, except for the essential `__init__.py` file.

### Linux / macOS (Bash)

```

```text
File created successfully: django_cleanup_commands.md

```bash
find . -path "*/migrations/*" -type f ! -name "__init__.py" -delete

```

### Windows (Command Prompt - CMD)

```cmd
FOR /F "delims=" %i IN ('dir /b /s /a:-d ^| findstr /i "\\migrations\\" ^| findstr /v /i "__init__.py"') DO del /q "%i"

```

### Windows (PowerShell)

```powershell
Get-ChildItem -Path . -Recurper -Filter *.py | Where-Object { $_.FullName -match '\\migrations\\' -and $_.Name -ne '__init__.py' } | Remove-Item -Force

```

---

## 2. Delete all `__pycache__` directories / Xóa toàn bộ thư mục `__pycache__`

This command searches and removes all Python bytecode cache directories (`__pycache__`) to force Python to recompile source files.

### Linux / macOS (Bash)

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +

```

### Windows (Command Prompt - CMD)

```cmd
FOR /F "delims=" %i IN ('dir /b /s /ad ^| findstr /i "__pycache__"') DO rmdir /s /q "%i"

```

### Windows (PowerShell)

```powershell
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

```

"""

file_path = "django_cleanup_commands.md"
with open(file_path, "w", encoding="utf-8") as f:
f.write(markdown_content)

print(f"File created successfully: {file_path}")

```
Tôi đã dịch nội dung sang tiếng Anh, bổ sung các câu lệnh tương ứng cho hệ điều hành Windows (bao gồm cả Command Prompt và PowerShell) và đóng gói tất cả vào một file Markdown (`.md`) rất trực quan, dễ sao chép.

Your MD file is ready
[file-tag: code-generated-file-0-1781749797707700861]

Dưới đây là nội dung chi tiết của file đã tạo để bạn có thể xem nhanh:

```markdown
# Django Cleanup Commands (Linux/macOS & Windows)

This document provides commands to clean up Django migration files and `__pycache__` directories for both Unix-like systems (Linux/macOS) and Windows (Command Prompt & PowerShell).

---

## 1. Delete all migration files, keeping `__init__.py` / Xóa tất cả file migration, giữ lại `__init__.py`

This command deletes all files inside `migrations` directories across your project, except for the essential `__init__.py` file.

### Linux / macOS (Bash)
```bash
find . -path "*/migrations/*" -type f ! -name "__init__.py" -delete

```

### Windows (Command Prompt - CMD)

```cmd
FOR /F "delims=" %i IN ('dir /b /s /a:-d ^| findstr /i "\\migrations\\" ^| findstr /v /i "__init__.py"') DO del /q "%i"

```

### Windows (PowerShell)

```powershell
Get-ChildItem -Path . -Recurse -Filter *.py | Where-Object { $_.FullName -match '\\migrations\\' -and $_.Name -ne '__init__.py' } | Remove-Item -Force

```

---

## 2. Delete all `__pycache__` directories / Xóa toàn bộ thư mục `__pycache__`

This command searches and removes all Python bytecode cache directories (`__pycache__`) to force Python to recompile source files.

### Linux / macOS (Bash)

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +

```

### Windows (Command Prompt - CMD)

```cmd
FOR /F "delims=" %i IN ('dir /b /s /ad ^| findstr /i "__pycache__"') DO rmdir /s /q "%i"

```

### Windows (PowerShell)

```powershell
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

```

```

```