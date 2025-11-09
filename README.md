# ValutaTrade Hub

Торговая платформа для криптовалют и фиатных валют.
Автор: Лазарев Виктор Самвелович.

## Установка

make install

## Запуск

make project

## Основные команды

**Регистрация и вход:**
- `register --username ИМЯ --password ПАРОЛЬ` - регистрация
- `login --username ИМЯ --password ПАРОЛЬ` - вход

**Торговля:**
- `buy --currency ВАЛЮТА --amount СУММА` - купить валюту
- `sell --currency ВАЛЮТА --amount СУММА` - продать валюту

**Портфель и курсы:**
- `show-portfolio` - показать портфель
- `get-rate --from ВАЛЮТА --to ВАЛЮТА` - получить курс
- `update-rates` - обновить курсы валют
- `show-rates` - показать кэшированные курсы

## Структура проекта

valutatrade_hub/
├── core/ # Бизнес-логика
│ ├── models.py # Модели данных (User, Wallet, Portfolio)
│ ├── usecases.py # Бизнес-сценарии
│ └── exceptions.py # Пользовательские исключения
├── cli/
│ └── interface.py # Командный интерфейс
├── parser_service/ # Сервис обновления курсов
│ ├── api_clients.py # Клиенты внешних API
│ ├── updater.py # Логика обновления курсов
│ └── storage.py # Хранение данных
├── infra/ # Инфраструктура
│ ├── settings.py # Настройки приложения
│ └── database.py # Управление данными
└── data/ # Файлы данных
├── users.json # Пользователи
├── portfolios.json # Портфели
└── rates.json # Курсы валют

# Кэш курсов

Курсы валют кэшируются в data/rates.json с TTL 300 секунд.
При устаревании курсов используется заглушка или можно обновить через update-rates.

## Parser Service

Сервис автоматически обновляет курсы валют из внешних API:

- **CoinGecko API** - для криптовалют (BTC, ETH, SOL)
- **ExchangeRate-API** - для фиатных валют (EUR, GBP, RUB)

## Демо c работой интерфейса и ошибками программы
https://asciinema.org/a/6Cs8eAiXfXnaf9AFibVdq9ZAZ
