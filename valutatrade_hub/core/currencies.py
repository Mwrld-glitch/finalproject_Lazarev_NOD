from valutatrade_hub.core.exceptions import CurrencyNotFoundError

def get_currency(code: str):
    """Простая заглушка для проверки валют"""
    supported_currencies = ['USD', 'EUR', 'BTC', 'ETH', 'RUB']
    if code.upper() not in supported_currencies:
        raise CurrencyNotFoundError(code)
    return code  # Просто возвращаем код валюты
