import os
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ParserConfig:
    # Ключ загружается из переменной окружения или используем твой
    EXCHANGERATE_API_KEY: str = os.getenv(
        "EXCHANGERATE_API_KEY", "735f02fa23769608a9917bbd"
    )

    # Эндпоинты
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # Списки валют
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple = field(default_factory=lambda: ("EUR", "GBP", "RUB"))
    CRYPTO_CURRENCIES: Tuple = field(default_factory=lambda: ("BTC", "ETH", "SOL"))
    CRYPTO_ID_MAP: Dict = field(
        default_factory=lambda: {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
        }
    )

    # Пути
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10


# Глобальный экземпляр конфига
config = ParserConfig()
