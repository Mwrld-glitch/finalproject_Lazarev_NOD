from valutatrade_hub.core import usecases
from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.parser_service.updater import rates_updater


def main():
    print("=== ValutaTrade Hub ===")
    print("Доступные команды:")
    print("")
    print("  Регистрация и вход:")
    print("  register --username ИМЯ --password ПАРОЛЬ")
    print("  login --username ИМЯ --password ПАРОЛЬ")
    print("")
    print("  Торговля:")
    print("  buy --currency ВАЛЮТА --amount СУММА")
    print("  sell --currency ВАЛЮТА --amount СУММА")
    print("")
    print("  Портфель и курсы:")
    print("  show-portfolio")
    print("  get-rate --from ВАЛЮТА --to ВАЛЮТА")
    print("  update-rates")
    print("  show-rates")
    print("")
    print("  Выход:")
    print("  exit")

    while True:
        command = input("Введите команду: ").strip()

        if command.startswith("register"):
            try:
                parts = command.split()
                if (
                    len(parts) == 5
                    and parts[1] == "--username"
                    and parts[3] == "--password"
                ):
                    username = parts[2]
                    password = parts[4]
                    user = usecases.register_user(username, password)
                    print(
                        f"Пользователь '{user.username}' зарегистрирован "
                        f"(id={user.user_id}). Войдите: login --username "
                        f"{user.username} --password ****"
                    )
                else:
                    print("Используйте: register --username NAME --password PASS")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command.startswith("login"):
            try:
                parts = command.split()
                if (
                    len(parts) == 5
                    and parts[1] == "--username"
                    and parts[3] == "--password"
                ):
                    username = parts[2]
                    password = parts[4]
                    user = usecases.login_user(username, password)
                    print(f"Вы вошли как '{user.username}'")
                else:
                    print("Используйте: login --username NAME --password PASS")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command == "show-portfolio":
            user = usecases.get_current_user()
            if not user:
                print("Сначала выполните login")
                continue
            try:
                display_data = usecases.get_portfolio_display(user.user_id)
                print(
                    f"Портфель пользователя '{user.username}' "
                    f"(база: {display_data['base_currency']}):"
                )
                if not display_data["wallets"]:
                    print("  У вас пока нет кошельков")
                    continue
                for wallet_display in display_data["wallets"]:
                    print(
                        f"  - {wallet_display['currency_code']}: "
                        f"{wallet_display['balance']:.2f} → "
                        f"{wallet_display['value_in_base']:.2f} "
                        f"{display_data['base_currency']}"
                    )
                print("  " + "-" * 40)
                print(
                    f"  ИТОГО: {display_data['total_value']:,.2f} "
                    f"{display_data['base_currency']}"
                )
            except CurrencyNotFoundError as e:
                print(f"Неизвестная базовая валюта '{e.code}'")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command.startswith("buy"):
            user = usecases.get_current_user()
            if not user:
                print("Сначала выполните login")
                continue

            parts = command.split()
            try:
                currency = parts[parts.index("--currency") + 1].upper()
                amount = float(parts[parts.index("--amount") + 1])
            except Exception:
                print("Используйте: buy --currency CODE --amount NUMBER")
                continue

            try:
                result = usecases.buy_currency(user.user_id, currency, amount)
                print(
                    f"Покупка выполнена: {result['amount']:.4f} {currency} "
                    f"по курсу {result['rate']:.2f} USD/{currency}"
                )
                print("Изменения в портфеле:")
                print(
                    f"  - {currency}: было {result['old_balance']:.4f} → "
                    f"стало {result['new_balance']:.4f}"
                )
                print(f"Оценочная стоимость покупки: {result['cost']:,.2f} USD")
            except CurrencyNotFoundError as e:
                print(f"Неизвестная валюта '{e.code}'")
            except ApiRequestError:
                print(f"Не удалось получить курс для {currency}→USD")
            except ValueError as e:
                error_msg = str(e)
                if "положительным" in error_msg:
                    print("'amount' должен быть положительным числом")
                else:
                    print(f"Ошибка: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command.startswith("sell"):
            user = usecases.get_current_user()
            if not user:
                print("Сначала выполните login")
                continue

            parts = command.split()
            try:
                currency = parts[parts.index("--currency") + 1].upper()
                amount = float(parts[parts.index("--amount") + 1])
            except Exception:
                print("Используйте: sell --currency CODE --amount NUMBER")
                continue

            try:
                result = usecases.sell_currency(user.user_id, currency, amount)
                print(
                    f"Продажа выполнена: {result['amount']:.4f} {currency} "
                    f"по курсу {result['rate']:.2f} USD/{currency}"
                )
                print("Изменения в портфеле:")
                print(
                    f"  - {currency}: было {result['old_balance']:.4f} → "
                    f"стало {result['new_balance']:.4f}"
                )
                print(f"Оценочная выручка: {result['revenue']:,.2f} USD")
            except CurrencyNotFoundError as e:
                print(f"Неизвестная валюта '{e.code}'")
            except InsufficientFundsError as e:
                print(str(e))
            except ValueError as e:
                error_msg = str(e)
                if "положительным" in error_msg:
                    print("'amount' должен быть положительным числом")
                elif "нет кошелька" in error_msg:
                    print(error_msg)
                else:
                    print(f"Ошибка: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command.startswith("get-rate"):
            parts = command.split()
            try:
                from_index = parts.index("--from")
                to_index = parts.index("--to")
                from_currency = parts[from_index + 1].upper()
                to_currency = parts[to_index + 1].upper()
            except Exception:
                print("Используйте: get-rate --from CODE --to CODE")
                continue

            try:
                result = usecases.get_exchange_rate(from_currency, to_currency)
                print(
                    f"Курс {result['from_currency']} → {result['to_currency']}: "
                    f"{result['rate']:.8f} (обновлено: {result['updated_at']})"
                )
                print(
                    f"Обратный курс {result['to_currency']}→ "
                    f"{result['from_currency']}: {result['reverse_rate']:.2f}"
                )
            except CurrencyNotFoundError as e:
                print(f"Неизвестная валюта '{e.code}'")
            except ApiRequestError:
                print(
                    f"Курс {from_currency} → {to_currency} недоступен. "
                    f"Повторите попытку позже."
                )
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command.startswith("update-rates"):
            print("INFO: Starting rates update...")

            success = rates_updater.run_update()
            if success:
                # Получаем количество обновленных курсов
                import json

                with open("data/rates.json", "r") as f:
                    rates_data = json.load(f)

                rate_count = 0
                for key in rates_data:
                    if key not in ["source", "last_refresh"]:
                        rate_count += 1

                last_refresh = rates_data.get("last_refresh", "неизвестно")
                print(
                    f"Update successful. Total rates updated: {rate_count}. "
                    f"Last refresh: {last_refresh}"
                )
            else:
                print(
                    "Update completed with errors. Check logs/parser.log for details."
                )

        elif command.startswith("show-rates"):
            try:
                # Загружаем курсы из файла
                import json
                import os

                if not os.path.exists("data/rates.json"):
                    print(
                        "Локональный кеш курсов пуст. Выполните 'update-rates', "
                        "чтобы загрузить данные."
                    )
                    continue

                with open("data/rates.json", "r") as f:
                    rates_data = json.load(f)

                # Базовая информация
                last_refresh = rates_data.get("last_refresh", "неизвестно")
                print(f"Rates from cache (updated at {last_refresh}):")

                # Фильтры
                currency_filter = None
                if "--currency" in command:
                    parts = command.split()
                    currency_index = parts.index("--currency")
                    currency_filter = parts[currency_index + 1].upper()

                # Собираем курсы для отображения
                display_rates = []
                for key, value in rates_data.items():
                    if key not in ["source", "last_refresh"] and isinstance(
                        value, dict
                    ):
                        if currency_filter is None or currency_filter in key:
                            display_rates.append((key, value["rate"]))

                if not display_rates:
                    if currency_filter:
                        print(f"Курс для '{currency_filter}' не найден в кеше.")
                    else:
                        print("Нет доступных курсов для отображения.")
                    continue

                if "--top" in command:
                    parts = command.split()
                    top_index = parts.index("--top")
                    top_count = int(parts[top_index + 1])
                    # Сортируем по убыванию курса (самые дорогие первые)
                    display_rates.sort(key=lambda x: x[1], reverse=True)
                    display_rates = display_rates[:top_count]
                else:
                    # По умолчанию сортируем по алфавиту
                    display_rates.sort(key=lambda x: x[0])

                # Вывод
                for currency_pair, rate in display_rates:
                    print(f"- {currency_pair}: {rate}")

            except Exception as e:
                print(f"Ошибка: {e}")

        elif command == "exit":
            break

        else:
            print(f"Команда '{command}' пока не реализована")


if __name__ == "__main__":
    main()
