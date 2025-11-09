class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get(self, key: str, default=None):
        # Простые настройки
        settings = {
            "data_path": "data/",
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
        }
        return settings.get(key, default)
