from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError

from .config import config


class BaseApiClient(ABC):
    """Абстрактный базовый класс для API клиентов"""

    @abstractmethod
    def fetch_rates(self) -> dict:
        """Возвращает курсы в формате {валютная_пара: курс}"""
        pass

    def _make_request(self, url: str) -> dict:
        """Общий метод для HTTP запросов"""
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Ошибка запроса к {url}: {str(e)}")


class CoinGeckoClient(BaseApiClient):
    """Клиент для CoinGecko API"""

    def fetch_rates(self) -> dict:
        crypto_ids = list(config.CRYPTO_ID_MAP.values())
        url = f"{config.COINGECKO_URL}?ids={','.join(crypto_ids)}&vs_currencies=usd"

        try:
            data = self._make_request(url)
            rates = {}

            for code, crypto_id in config.CRYPTO_ID_MAP.items():
                if crypto_id in data and "usd" in data[crypto_id]:
                    rate = data[crypto_id]["usd"]
                    rates[f"{code}_USD"] = rate
                    rates[f"USD_{code}"] = 1 / rate

            return rates
        except ApiRequestError:
            return {}


class ExchangeRateApiClient(BaseApiClient):
    """Клиент для ExchangeRate-API"""

    def fetch_rates(self) -> dict:
        url = (
            f"{config.EXCHANGERATE_API_URL}/{config.EXCHANGERATE_API_KEY}/"
            f"latest/{config.BASE_CURRENCY}"
        )
        
        try:
            data = self._make_request(url)

            if data.get("result") != "success":
                raise ApiRequestError(
                    f"API error: {data.get('error-type', 'Unknown error')}"
                )

            rates = {}
            base_rates = data["conversion_rates"]

            for currency in config.FIAT_CURRENCIES:
                if currency in base_rates:
                    rate = base_rates[currency]
                    rates[f"{currency}_USD"] = rate
                    rates[f"USD_{currency}"] = 1 / rate

            return rates
        except ApiRequestError:
            return {}