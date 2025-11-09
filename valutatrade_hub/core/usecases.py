import json
import os
from datetime import datetime, timedelta

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    InsufficientFundsError,
)
from valutatrade_hub.core.models import Portfolio, User
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.settings import SettingsLoader

settings = SettingsLoader()
_current_user = None


def _load_json_file(file_path):
    """Универсальная загрузка JSON файла"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    with open(file_path, "r") as f:
        return json.load(f)


def _save_json_file(file_path, data):
    """Универсальное сохранение в JSON файл"""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


@log_action(action="REGISTER")
def register_user(username: str, password: str) -> User:
    data_path = settings.get("data_path", "data/")
    users_file = os.path.join(data_path, "users.json")
    os.makedirs(data_path, exist_ok=True)

    try:
        users = _load_json_file(users_file)

        if any(user["username"] == username for user in users):
            raise ValueError(f"Имя пользователя '{username}' уже занято")

        user_id = max((user["user_id"] for user in users), default=0) + 1
        user = User.create_new(user_id, username, password)

        users.append(user.to_dict())
        _save_json_file(users_file, users)

        # Создаем пустой портфель
        portfolios_file = os.path.join(data_path, "portfolios.json")
        portfolios = _load_json_file(portfolios_file)
        portfolios.append({"user_id": user_id, "wallets": {}})
        _save_json_file(portfolios_file, portfolios)

        return user

    except Exception as e:
        raise ApiRequestError(f"Ошибка при регистрации: {str(e)}")


@log_action(action="LOGIN")
def login_user(username: str, password: str) -> User:
    global _current_user

    data_path = settings.get("data_path", "data/")
    users_file = os.path.join(data_path, "users.json")

    if not os.path.exists(users_file):
        raise ValueError(f"Пользователь '{username}' не найден")

    try:
        users = _load_json_file(users_file)

        for user_data in users:
            if user_data["username"] == username:
                user = User.from_dict(user_data)
                if user.verify_password(password):
                    _current_user = user
                    return user
                raise ValueError("Неверный пароль")

        raise ValueError(f"Пользователь '{username}' не найден")

    except Exception as e:
        raise ApiRequestError(f"Ошибка при входе: {str(e)}")


def get_current_user():
    return _current_user


def logout_user():
    global _current_user
    _current_user = None


def get_user_portfolio(user_id: int) -> Portfolio:
    data_path = settings.get("data_path", "data/")
    portfolios_file = os.path.join(data_path, "portfolios.json")

    if not os.path.exists(portfolios_file):
        return Portfolio(user_id, {})

    try:
        portfolios = _load_json_file(portfolios_file)
        for portfolio_data in portfolios:
            if portfolio_data["user_id"] == user_id:
                return Portfolio.from_dict(portfolio_data)
        return Portfolio(user_id, {})

    except Exception as e:
        raise ApiRequestError(f"Ошибка при загрузке портфеля: {str(e)}")


def get_portfolio_display(user_id: int, base_currency: str = None) -> dict:
    base_currency = base_currency or settings.get("default_base_currency", "USD")
    get_currency(base_currency)  # Валидация

    portfolio = get_user_portfolio(user_id)
    total_value = portfolio.get_total_value(base_currency)

    wallets_display = []
    for currency_code, wallet in portfolio.wallets.items():
        value_in_base = (
            wallet.balance
            if currency_code == base_currency
            else Portfolio(user_id, {currency_code: wallet}).get_total_value(
                base_currency
            )
        )
        wallets_display.append(
            {
                "currency_code": currency_code,
                "balance": wallet.balance,
                "value_in_base": value_in_base,
            }
        )

    return {
        "base_currency": base_currency,
        "total_value": total_value,
        "wallets": wallets_display,
    }


@log_action(action="BUY", verbose=True)
def buy_currency(user_id: int, currency_code: str, amount: float) -> dict:
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")

    get_currency(currency_code)  # Валидация

    portfolio = get_user_portfolio(user_id)
    if currency_code not in portfolio.wallets:
        portfolio.add_currency(currency_code)

    rate_data = get_exchange_rate(currency_code, "USD")
    rate = rate_data["rate"]

    wallet = portfolio.get_wallet(currency_code)
    old_balance = wallet.balance
    wallet.deposit(amount)
    save_portfolio(portfolio)

    return {
        "amount": amount,
        "rate": rate,
        "old_balance": old_balance,
        "new_balance": wallet.balance,
        "cost": amount * rate,
    }


@log_action(action="SELL", verbose=True)
def sell_currency(user_id: int, currency_code: str, amount: float) -> dict:
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")

    get_currency(currency_code)  # Валидация

    portfolio = get_user_portfolio(user_id)
    if currency_code not in portfolio.wallets:
        raise ValueError(
            f"У вас нет кошелька '{currency_code}'. Добавьте валюту: "
            f"она создаётся автоматически при первой покупке."
        )

    rate_data = get_exchange_rate(currency_code, "USD")
    rate = rate_data["rate"]

    wallet = portfolio.get_wallet(currency_code)
    old_balance = wallet.balance

    if amount > wallet.balance:
        raise InsufficientFundsError(wallet.balance, amount, currency_code)

    wallet.withdraw(amount)
    save_portfolio(portfolio)

    return {
        "amount": amount,
        "rate": rate,
        "old_balance": old_balance,
        "new_balance": wallet.balance,
        "revenue": amount * rate,
    }


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    get_currency(from_currency)  # Валидация
    get_currency(to_currency)  # Валидация

    ttl_seconds = settings.get("rates_ttl_seconds", 300)
    data_path = settings.get("data_path", "data/")
    rates_file = os.path.join(data_path, "rates.json")

    if os.path.exists(rates_file):
        try:
            rates_data = _load_json_file(rates_file)
            rate_key = f"{from_currency}_{to_currency}"
            if rate_key in rates_data:
                rate_info = rates_data[rate_key]
                updated_at = datetime.fromisoformat(rate_info["updated_at"])
                if datetime.now() - updated_at <= timedelta(seconds=ttl_seconds):
                    reverse_rate = 1 / rate_info["rate"]
                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "rate": rate_info["rate"],
                        "updated_at": rate_info["updated_at"],
                        "reverse_rate": reverse_rate,
                    }
        except Exception:
            pass

    stub_rates = {
        "EUR_USD": 1.0786,
        "BTC_USD": 59337.21,
        "USD_BTC": 0.00001685,
        "USD_EUR": 0.93,
        "ETH_USD": 3720.00,
    }

    rate_key = f"{from_currency}_{to_currency}"
    if rate_key in stub_rates:
        rate = stub_rates[rate_key]
    else:
        reverse_key = f"{to_currency}_{from_currency}"
        if reverse_key in stub_rates:
            rate = 1 / stub_rates[reverse_key]
        else:
            raise ApiRequestError(f"Курс {from_currency}→{to_currency} недоступен")

    # Сохраняем в кеш
    try:
        rates_data = _load_json_file(rates_file) if os.path.exists(rates_file) else {}
        rates_data[rate_key] = {"rate": rate, "updated_at": datetime.now().isoformat()}
        rates_data["last_refresh"] = datetime.now().isoformat()
        _save_json_file(rates_file, rates_data)
    except Exception:
        pass

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": rate,
        "updated_at": datetime.now().isoformat(),
        "reverse_rate": 1 / rate,
    }


def save_portfolio(portfolio: Portfolio):
    data_path = settings.get("data_path", "data/")
    portfolios_file = os.path.join(data_path, "portfolios.json")

    try:
        portfolios = (
            _load_json_file(portfolios_file) if os.path.exists(portfolios_file) else []
        )

        for i, p in enumerate(portfolios):
            if p["user_id"] == portfolio.user_id:
                portfolios[i] = portfolio.to_dict()
                break
        else:
            portfolios.append(portfolio.to_dict())

        _save_json_file(portfolios_file, portfolios)

    except Exception as e:
        raise ApiRequestError(f"Ошибка при сохранении портфеля: {str(e)}")
