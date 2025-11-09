import json
import os


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_json(self, file_path):
        """Загружает данные из JSON файла"""
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return []
        with open(file_path, "r") as f:
            return json.load(f)

    def save_json(self, file_path, data):
        """Сохраняет данные в JSON файл"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
