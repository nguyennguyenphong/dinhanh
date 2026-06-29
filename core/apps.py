import os
import json
from django.apps import AppConfig
from django.conf import settings

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            self.generate_project_structure()

    def generate_project_structure(self):
        root_dir = settings.BASE_DIR
        EXCLUDE_DIRS = {'migrations', '__pycache__', '.git', '.venv', 'venv', 'node_modules', 'staticfiles'}
        EXCLUDE_EXTENSIONS = {
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
            '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.md', '.txt',
            '.mp4', '.avi', '.mkv', '.mov', '.pyc'
        }

        def build_tree(current_path):
            tree = {}
            files_list = []

            try:
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    
                    if os.path.isdir(item_path):
                        if item in EXCLUDE_DIRS:
                            continue
                        sub_tree = build_tree(item_path)
                        if sub_tree:
                            tree[item] = sub_tree

                    elif os.path.isfile(item_path):
                        if item == '__init__.py':
                            continue
                        _, ext = os.path.splitext(item.lower())
                        if ext in EXCLUDE_EXTENSIONS:
                            continue
                        files_list.append(item)
            except PermissionError:
                pass

            if files_list and tree:
                tree["_files"] = files_list
                return tree
            if files_list and not tree:
                return files_list
            return tree

        root_name = os.path.basename(root_dir)
        project_structure = {
            root_name: build_tree(root_dir)
        }

        output_path = os.path.join(root_dir, 'init.json')
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(project_structure, json_file, ensure_ascii=False, indent=2)
            