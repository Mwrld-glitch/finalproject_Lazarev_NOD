import hashlib
from datetime import datetime


class User:
    def __init__(
        self,
        user_id: int,
        username: str,
        hashed_password: str,
        salt: str,
        registration_date: str,
    ):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value

    def get_user_info(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date,
        }

    def change_password(self, new_password: str):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._hashed_password = hashlib.sha256(
            (new_password + self._salt).encode()
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        test_hash = hashlib.sha256((password + self._salt).encode()).hexdigest()
        return self._hashed_password == test_hash

    def to_dict(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date,
        }

    @classmethod
    def create_new(cls, user_id: int, username: str, password: str):
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")

        salt = hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        registration_date = datetime.now().isoformat()

        return cls(user_id, username, hashed_password, salt, registration_date)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=data["registration_date"],
        )


class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = currency_code
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = value

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self.balance:
            raise ValueError(
                f"Недостаточно средств. Доступно: {self.balance} {self.currency_code}"
            )
        self.balance -= amount

    def get_balance_info(self) -> dict:
        return {"currency_code": self.currency_code, "balance": self.balance}

    def to_dict(self) -> dict:
        return {"currency_code": self.currency_code, "balance": self.balance}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(currency_code=data["currency_code"], balance=data["balance"])


class Portfolio:
    def __init__(self, user_id: int, wallets: dict = None):
        self._user_id = user_id
        self._wallets = wallets or {}

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> dict:
        return self._wallets.copy()

    def add_currency(self, currency_code: str):
        if currency_code in self._wallets:
            raise ValueError(f"Кошелек для валюты {currency_code} уже существует")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code: str) -> Wallet:
        if currency_code not in self._wallets:
            raise ValueError(f"Кошелек для валюты {currency_code} не найден")
        return self._wallets[currency_code]

    def get_total_value(self, base_currency: str = "USD") -> float:
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
        wallets_dict = {}
        for currency_code, wallet in self._wallets.items():
            wallets_dict[currency_code] = wallet.to_dict()

        return {"user_id": self._user_id, "wallets": wallets_dict}

    @classmethod
    def from_dict(cls, data: dict):
        wallets = {}
        for currency_code, wallet_data in data["wallets"].items():
            wallets[currency_code] = Wallet.from_dict(wallet_data)

        return cls(user_id=data["user_id"], wallets=wallets)
