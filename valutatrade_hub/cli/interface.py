from valutatrade_hub.core import usecases
from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError, InsufficientFundsError, ApiRequestError
)


def main():
    print("=== ValutaTrade Hub ===")
    print("Доступные команды:")
    print("  register --username NAME --password PASS")
    print("  login --username NAME --password PASS")
    print("  show-portfolio")
    print("  buy --currency CODE --amount NUMBER")
    print("  sell --currency CODE --amount NUMBER")
    print("  get-rate --from CODE --to CODE")
    print("  exit")
    
    while True:
        command = input("Введите команду: ").strip()
        
        if command.startswith("register"):
            try:
                parts = command.split()
                if len(parts) == 5 and parts[1] == "--username" and parts[3] == "--password":
                    username = parts[2]
                    password = parts[4]
                    user = usecases.register_user(username, password)
                    print(f"Пользователь '{user.username}' зарегистрирован (id={user.user_id}). Войдите: login --username {user.username} --password ****")
                else:
                    print("Используйте: register --username NAME --password PASS")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif command.startswith("login"):
            try:
                parts = command.split()
                if len(parts) == 5 and parts[1] == "--username" and parts[3] == "--password":
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
                print(f"Портфель пользователя '{user.username}' (база: {display_data['base_currency']}):")
                if not display_data["wallets"]:
                    print("  У вас пока нет кошельков")
                    continue
                for wallet_display in display_data["wallets"]:
                    print(f"  - {wallet_display['currency_code']}: {wallet_display['balance']:.2f} → {wallet_display['value_in_base']:.2f} {display_data['base_currency']}")
                print("  " + "-" * 40)
                print(f"  ИТОГО: {display_data['total_value']:,.2f} {display_data['base_currency']}")
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
            except:
                print("Используйте: buy --currency CODE --amount NUMBER")
                continue
            
            try:
                result = usecases.buy_currency(user.user_id, currency, amount)
                print(f"Покупка выполнена: {result['amount']:.4f} {currency} по курсу {result['rate']:.2f} USD/{currency}")
                print("Изменения в портфеле:")
                print(f"  - {currency}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}")
                print(f"Оценочная стоимость покупки: {result['cost']:,.2f} USD")
            except CurrencyNotFoundError as e:
                print(f"Неизвестная валюта '{e.code}'")
            except ApiRequestError as e:
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
            except:
                print("Используйте: sell --currency CODE --amount NUMBER")
                continue
            
            try:
                result = usecases.sell_currency(user.user_id, currency, amount)
                print(f"Продажа выполнена: {result['amount']:.4f} {currency} по курсу {result['rate']:.2f} USD/{currency}")
                print("Изменения в портфеле:")
                print(f"  - {currency}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}")
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
            except:
                print("Используйте: get-rate --from CODE --to CODE")
                continue
            
            try:
                result = usecases.get_exchange_rate(from_currency, to_currency)
                print(f"Курс {result['from_currency']}→{result['to_currency']}: {result['rate']:.8f} (обновлено: {result['updated_at']})")
                print(f"Обратный курс {result['to_currency']}→{result['from_currency']}: {result['reverse_rate']:.2f}")
            except CurrencyNotFoundError as e:
                print(f"Неизвестная валюта '{e.code}'")
            except ApiRequestError as e:
                print(f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже.")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif command == "exit":
            break
            
        else:
            print(f"Команда '{command}' пока не реализована")

if __name__ == "__main__":
    main()