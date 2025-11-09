from datetime import datetime

from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .storage import RatesStorage


class RatesUpdater:
    """Основной класс для обновления курсов"""

    def __init__(self):
        self.coingecko_client = CoinGeckoClient()
        self.exchangerate_client = ExchangeRateApiClient()
        self.storage = RatesStorage()

    def run_update(self) -> bool:
        """Запускает полное обновление курсов"""
        all_rates = {}
        success_sources = 0

        # Получаем курсы от обоих API
        try:
            crypto_rates = self.coingecko_client.fetch_rates()
            if crypto_rates:
                all_rates.update(crypto_rates)
                print(
                    f"INFO: Fetching from CoinGecko... OK ({len(crypto_rates)} rates)"
                )
                success_sources += 1
            else:
                print("ERROR: Failed to fetch from CoinGecko: No data received")
        except Exception as e:
            print(f"ERROR: Failed to fetch from CoinGecko: {e}")

        try:
            fiat_rates = self.exchangerate_client.fetch_rates()
            if fiat_rates:
                all_rates.update(fiat_rates)
                print(
                    f"INFO: Fetching from ExchangeRate-API... OK "
                    f"({len(fiat_rates)} rates)"
                )
                success_sources += 1
            else:
                print("ERROR: Failed to fetch from ExchangeRate-API: No data received")
        except Exception as e:
            print(f"ERROR: Failed to fetch from ExchangeRate-API: {e}")

        if not all_rates:
            return False

        # Сохраняем текущие курсы
        current_rates_data = {}
        for currency_pair, rate in all_rates.items():
            current_rates_data[currency_pair] = {
                "rate": rate,
                "updated_at": datetime.now().isoformat(),
                "source": (
                    "CoinGecko"
                    if any(crypto in currency_pair for crypto in ["BTC", "ETH", "SOL"])
                    else "ExchangeRate-API"
                ),
            }

            # Сохраняем историческую запись
            source = (
                "CoinGecko"
                if any(crypto in currency_pair for crypto in ["BTC", "ETH", "SOL"])
                else "ExchangeRate-API"
            )
            self.storage.save_historical_record(currency_pair, rate, source)

        # Сохраняем текущие курсы
        if self.storage.save_current_rates(current_rates_data):
            print(f"INFO: Writing {len(all_rates)} rates to data/rates.json...")
            return success_sources == 2
        else:
            return False


# Глобальный экземпляр
rates_updater = RatesUpdater()
