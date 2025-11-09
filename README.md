## ValutaTrade Hub

Торговая платформа для криптовалют и фиатных валют

# Автор

Лазарев Виктор Самвелович

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

- `valutatrade_hub/core/` - бизнес-логика (модели, usecases)
- `valutatrade_hub/cli/` - интерфейс командной строки  
- `valutatrade_hub/parser_service/` - сервис обновления курсов
- `valutatrade_hub/infra/` - инфраструктура (настройки, БД)
- `data/` - файлы данных (пользователи, портфели, курсы)

# Кэш курсов

Курсы валют кэшируются в data/rates.json с TTL 300 секунд.
При устаревании курсов используется заглушка или можно обновить через update-rates.

## Parser Service

Сервис автоматически обновляет курсы валют из внешних API:

- **CoinGecko API** - для криптовалют (BTC, ETH, SOL)
- **ExchangeRate-API** - для фиатных валют (EUR, GBP, RUB)

## Демо c работой интерфейса и ошибками программы
https://asciinema.org/a/6Cs8eAiXfXnaf9AFibVdq9ZAZ
