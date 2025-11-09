import hashlib
from datetime import datetime


class User:
    """Класс пользователя торговой системы."""
    
    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: str,
    ):
        # Валидация при создании
        if not username or len(username.strip()) < 3:
            raise ValueError("Имя пользователя должно быть не короче 3 символов")
        if len(hashed_password) < 8:
            raise ValueError("Некорректный хеш пароля")
        if not salt or len(salt) < 4:
            raise ValueError("Некорректная соль")
            
        self._user_id = user_id
        self._username = username.strip()
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        """Возвращает идентификатор пользователя."""
        return self._user_id

    @property
    def username(self) -> str:
        """Возвращает имя пользователя."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Устанавливает имя пользователя с валидацией."""
        if not value or len(value.strip()) < 3:
            raise ValueError("Имя пользователя должно быть не короче 3 символов")
        self._username = value.strip()

    def get_user_info(self) -> dict:
        """Возвращает информацию о пользователе (без пароля)."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date,
        }

    def change_password(self, new_password: str):
        """Изменяет пароль пользователя с валидацией."""
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._hashed_password = hashlib.sha256(
            (new_password + self._salt).encode()
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Проверяет соответствие пароля."""
        test_hash = hashlib.sha256((password + self._salt).encode()).hexdigest()
        return self._hashed_password == test_hash

    def to_dict(self) -> dict:
        """Сериализует пользователя в словарь."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date,
        }

    @classmethod
    def create_new(cls, user_id: int, username: str, password: str):
        """Создает нового пользователя."""
        if not username or len(username.strip()) < 3:
            raise ValueError("Имя пользователя должно быть не короче 3 символов")
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")

        salt = hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        registration_date = datetime.now().isoformat()

        return cls(user_id, username.strip(), hashed_password, salt, registration_date)

    @classmethod
    def from_dict(cls, data: dict):
        """Создает пользователя из словаря."""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=data["registration_date"],
        )


class Wallet:
    """Класс кошелька для хранения средств в определенной валюте."""
    
    def __init__(self, currency_code: str, balance: float = 0.0):
        if not currency_code or len(currency_code) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")
            
        self.currency_code = currency_code.upper()
        self._balance = float(balance)

    @property
    def balance(self) -> float:
        """Возвращает текущий баланс кошелька."""
        return self._balance

    @balance.setter
    def balance(self, value: float):
        """Устанавливает баланс с валидацией."""
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    def deposit(self, amount: float):
        """Пополняет баланс кошелька."""
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount

    def withdraw(self, amount: float):
        """Снимает средства с кошелька."""
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self.balance:
            raise ValueError(
                f"Недостаточно средств. Доступно: {self.balance:.4f} "
                f"{self.currency_code}"
            )
        self.balance -= amount

    def get_balance_info(self) -> dict:
        """Возвращает информацию о балансе."""
        return {"currency_code": self.currency_code, "balance": self.balance}

    def to_dict(self) -> dict:
        """Сериализует кошелек в словарь."""
        return {"currency_code": self.currency_code, "balance": self.balance}

    @classmethod
    def from_dict(cls, data: dict):
        """Создает кошелек из словаря."""
        return cls(currency_code=data["currency_code"], balance=data["balance"])


class Portfolio:
    """Класс портфеля пользователя, содержащий коллекцию кошельков."""
    
    def __init__(self, user_id: int, wallets: dict = None):
        if user_id <= 0:
            raise ValueError("ID пользователя должен быть положительным")
            
        self._user_id = user_id
        self._wallets = wallets or {}

    @property
    def user_id(self) -> int:
        """Возвращает идентификатор пользователя."""
        return self._user_id

    @property
    def wallets(self) -> dict:
        """Возвращает копию словаря кошельков."""
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        """Добавляет новую валюту в портфель."""
        if not currency_code or len(currency_code) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")
        currency_code = currency_code.upper()
        
        if currency_code in self._wallets:
            raise ValueError(f"Кошелек для валюты {currency_code} уже существует")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet:
        """Возвращает кошелек по коду валюты."""
        if not currency_code or len(currency_code) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")
        currency_code = currency_code.upper()
        
        if currency_code not in self._wallets:
            raise ValueError(f"Кошелек для валюты {currency_code} не найден")
        return self._wallets[currency_code]

    def get_total_value(self, base_currency: str = "USD") -> float:
        """Рассчитывает общую стоимость портфеля в базовой валюте."""
        if not base_currency or len(base_currency) != 3:
            raise ValueError("Код базовой валюты должен состоять из 3 символов")
        base_currency = base_currency.upper()

        exchange_rates = {
            "USD_USD": 1.0,
            "EUR_USD": 1.08,
            "BTC_USD": 50000.0,
            "ETH_USD": 3000.0,
            "RUB_USD": 0.011,
        }

        total_value = 0.0

        for currency_code, wallet in self._wallets.items():
            if currency_code == base_currency:
                total_value += wallet.balance
            else:
                rate_key = f"{currency_code}_{base_currency}"
                if rate_key in exchange_rates:
                    total_value += wallet.balance * exchange_rates[rate_key]

        return total_value

    def to_dict(self) -> dict:
        """Сериализует портфель в словарь."""
        wallets_dict = {}
        for currency_code, wallet in self._wallets.items():
            wallets_dict[currency_code] = wallet.to_dict()

        return {"user_id": self._user_id, "wallets": wallets_dict}

    @classmethod
    def from_dict(cls, data: dict):
        """Создает портфель из словаря."""
        wallets = {}
        for currency_code, wallet_data in data["wallets"].items():
            wallets[currency_code] = Wallet.from_dict(wallet_data)

        return cls(user_id=data["user_id"], wallets=wallets)