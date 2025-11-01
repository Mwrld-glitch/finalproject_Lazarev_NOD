import json
import os
from valutatrade_hub.core.models import User


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