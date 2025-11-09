# ValutaTrade Hub

Торговая платформа для криптовалют и фиатных валют.
Автор: Лазарев Виктор Самвелович.

## Установка

make install

## Запуск

make project

# Основные команды

register --username NAME --password PASS - регистрация

login --username NAME --password PASS - вход

show-portfolio - показать портфель

buy --currency CODE --amount NUMBER - купить валюту

sell --currency CODE --amount NUMBER - продать валюту

get-rate --from CODE --to CODE - получить курс

update-rates - обновить курсы валют

show-rates - показать кэшированные курсы

# Структура проекта
valutatrade_hub/
├── core/           # Бизнес-логика (модели, usecases)
├── cli/            # Интерфейс командной строки
├── parser_service/ # Сервис обновления курсов
├── infra/          # Инфраструктура (настройки, БД)
└── data/           # Данные (пользователи, портфели, курсы)

# Кэш курсов

Курсы валют кэшируются в data/rates.json с TTL 300 секунд.
При устаревании курсов используется заглушка или можно обновить через update-rates.

## Parser Service

Сервис автоматически обновляет курсы валют из внешних API:

- **CoinGecko API** - для криптовалют (BTC, ETH, SOL)
- **ExchangeRate-API** - для фиатных валют (EUR, GBP, RUB)

## Демо c работой интерфейса и ошибками программы
https://asciinema.org/a/6Cs8eAiXfXnaf9AFibVdq9ZAZ
