class CurrencyNotFoundError(Exception):
    """Исключение: валюта не найдена в системе."""
    
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Неизвестная валюта '{code}'")


class InsufficientFundsError(Exception):
    """Исключение: недостаточно средств для операции."""
    
    def __init__(self, available: float, required: float, code: str):
        super().__init__(
            f"Недостаточно средств: доступно {available} {code}, "
            f"требуется {required} {code}"
        )


class ApiRequestError(Exception):
    """Исключение: ошибка при обращении к внешнему API."""
    
    def __init__(self, reason: str):
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")