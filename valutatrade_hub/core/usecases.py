import json
import os

from valutatrade_hub.core.models import Portfolio, User

"""Бизнес-логика регистрации пользователя"""
def register_user(username: str, password: str) -> User:
    # Проверяем уникальность username
    users_file = "data/users.json"
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(users_file) or os.path.getsize(users_file) == 0:
        users = []
    else:
        with open(users_file, "r") as f:
            users = json.load(f)
    
    # Проверка уникальности
    for user_data in users:
        if user_data["username"] == username:
            raise ValueError(f"Имя пользователя '{username}' уже занято")
    
    # Генерируем ID (автоинкремент)
    if users:
        user_id = max(user["user_id"] for user in users) + 1
    else:
        user_id = 1
    
    # Создаем пользователя
    user = User.create_new(user_id, username, password)
    
    # Сохраняем пользователя
    users.append(user.to_dict())
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)
    
    # Создаем пустой портфель
    portfolios_file = "data/portfolios.json"
    if not os.path.exists(portfolios_file) or os.path.getsize(portfolios_file) == 0:
        portfolios = []
    else:
        with open(portfolios_file, "r") as f:
            portfolios = json.load(f)
    
    portfolio = {"user_id": user_id, "wallets": {}}
    portfolios.append(portfolio)
    with open(portfolios_file, "w") as f:
        json.dump(portfolios, f, indent=2)
    
    return user

"""Бизнес-логика на логин пользователя"""
_current_user = None  # Текущий пользователь (сессия)

def login_user(username: str, password: str) -> User:
    global _current_user
    
    users_file = "data/users.json"
    if not os.path.exists(users_file):
        raise ValueError(f"Пользователь '{username}' не найден")
    
    with open(users_file, "r") as f:
        users = json.load(f)
    
    for user_data in users:
        if user_data["username"] == username:
            user = User.from_dict(user_data)
            if user.verify_password(password):
                _current_user = user
                return user
            else:
                raise ValueError("Неверный пароль")
    
    raise ValueError(f"Пользователь '{username}' не найден")

def get_current_user():
    """Возвращает текущего пользователя"""
    return _current_user

def logout_user():
    """Выход пользователя"""
    global _current_user
    _current_user = None

"""Бизнес-логика получения портфеля пользователя"""
def get_user_portfolio(user_id: int) -> Portfolio:
    """Загружает портфель пользователя из файла"""
    portfolios_file = "data/portfolios.json"
    
    if not os.path.exists(portfolios_file):
        return Portfolio(user_id, {})
    
    with open(portfolios_file, "r") as f:
        portfolios = json.load(f)
    
    for portfolio_data in portfolios:
        if portfolio_data["user_id"] == user_id:
            return Portfolio.from_dict(portfolio_data)
    
    # Если портфель не найден, создаем пустой
    return Portfolio(user_id, {})

def get_portfolio_display(user_id: int, base_currency: str = "USD") -> dict:
    # Проверяем что базовая валюта поддерживается
    supported_currencies = ['USD', 'EUR', 'BTC', 'ETH', 'RUB']
    if base_currency not in supported_currencies:
        raise ValueError(f"Неизвестная базовая валюта '{base_currency}'")
    
    portfolio = get_user_portfolio(user_id)
    total_value = portfolio.get_total_value(base_currency)
    
    wallets_display = []
    for currency_code, wallet in portfolio.wallets.items():
        if currency_code == base_currency:
            value_in_base = wallet.balance
        else:
            temp_portfolio = Portfolio(user_id, {currency_code: wallet})
            value_in_base = temp_portfolio.get_total_value(base_currency)
            
        wallets_display.append({
            "currency_code": currency_code,
            "balance": wallet.balance,
            "value_in_base": value_in_base
        })
    
    return {
        "base_currency": base_currency,
        "total_value": total_value,
        "wallets": wallets_display
    }



def buy_currency(user_id: int, currency: str, amount: float) -> dict:
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    
    portfolio = get_user_portfolio(user_id)
    
    if currency not in portfolio.wallets:
        portfolio.add_currency(currency)
    
    rates = {"BTC": 59300.00, "ETH": 3200.00, "EUR": 1.07}
    if currency not in rates:
        raise ValueError(f"Не удалось получить курс для {currency}→USD")
    
    rate = rates[currency]
    wallet = portfolio.get_wallet(currency)
    old_balance = wallet.balance
    wallet.deposit(amount)
    
    save_portfolio(portfolio)
    
    return {
        'amount': amount,
        'rate': rate,
        'old_balance': old_balance,
        'new_balance': wallet.balance,
        'cost': amount * rate
    }

def save_portfolio(portfolio: Portfolio):
    portfolios_file = "data/portfolios.json"
    
    if os.path.exists(portfolios_file):
        with open(portfolios_file, "r") as f:
            portfolios = json.load(f)
    else:
        portfolios = []
    
    for i, p in enumerate(portfolios):
        if p["user_id"] == portfolio.user_id:
            portfolios[i] = portfolio.to_dict()
            break
    else:
        portfolios.append(portfolio.to_dict())
    
    with open(portfolios_file, "w") as f:
        json.dump(portfolios, f, indent=2)



def sell_currency(user_id: int, currency: str, amount: float) -> dict:
    if amount <= 0:
        raise ValueError("'amount' должен быть положительным числом")
    
    portfolio = get_user_portfolio(user_id)
    
    if currency not in portfolio.wallets:
        raise ValueError(f"У вас нет кошелька '{currency}'. Добавьте валюту: она создаётся автоматически при первой покупке.")
    
    rates = {"BTC": 59800.00, "ETH": 3200.00, "EUR": 1.07, "USD": 1.0}
    if currency not in rates:
        raise ValueError(f"Не удалось получить курс для {currency}→USD")
    
    rate = rates[currency]
    wallet = portfolio.get_wallet(currency)
    old_balance = wallet.balance
    
    if amount > wallet.balance:
        raise ValueError(f"Недостаточно средств: доступно {wallet.balance:.4f} {currency}, требуется {amount:.4f} {currency}")
    
    wallet.withdraw(amount)
    
    save_portfolio(portfolio)
    
    return {
        'amount': amount,
        'rate': rate,
        'old_balance': old_balance,
        'new_balance': wallet.balance,
        'revenue': amount * rate
    }


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    from datetime import datetime, timedelta
    
    # Шаг 1: Проверка валют
    if not from_currency or not to_currency:
        raise ValueError("Коды валют не могут быть пустыми")
    
    # Шаг 2: Пробуем rates.json
    rates_file = "data/rates.json"
    if os.path.exists(rates_file):
        with open(rates_file, "r") as f:
            rates_data = json.load(f)
        
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key in rates_data:
            rate_info = rates_data[rate_key]
            # Проверка свежести
            updated_at = datetime.fromisoformat(rate_info["updated_at"])
            if datetime.now() - updated_at <= timedelta(minutes=5):
                # Курс свежий - возвращаем
                return _calculate_rates(from_currency, to_currency, rate_info["rate"])
    
    # Заглушка если rates.json недоступен или курс устарел
    stub_rates = {
        "EUR_USD": 1.0786,
        "BTC_USD": 59337.21,
        "RUB_USD": 0.01016, 
        "ETH_USD": 3720.00
    }
    
    # Ищем в заглушке
    rate_key = f"{from_currency}_{to_currency}"
    if rate_key in stub_rates:
        return _calculate_rates(from_currency, to_currency, stub_rates[rate_key])
    
    reverse_key = f"{to_currency}_{from_currency}" 
    if reverse_key in stub_rates:
        reverse_rate = stub_rates[reverse_key]
        rate = 1 / reverse_rate
        return _calculate_rates(from_currency, to_currency, rate)
    
    # Ошибка если курс не найден
    raise ValueError(f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже.")

def _calculate_rates(from_currency, to_currency, rate):
    """Вычисляет прямые и обратные курсы"""
    return {
        'from_currency': from_currency,
        'to_currency': to_currency,
        'rate': rate,
        'updated_at': "2025-10-09T10:30:00",
        'reverse_rate': 1 / rate
    }