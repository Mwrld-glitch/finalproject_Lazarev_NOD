from valutatrade_hub.core import usecases

def main():
    print("=== ValutaTrade Hub ===")
    print("Доступные команды:")
    print("  register --username NAME --password PASS")
    print("  login --username NAME --password PASS")
    print("  show-portfolio")
    print("  buy")
    print("  sell")
    print("  get-rate")
    print("  exit")
    
    while True:
        command = input("Введите команду: ").strip()
        
        # Команда register
        if command.startswith("register"):
            try:
                parts = command.split()
                if len(parts) == 5 and parts[1] == "--username" and parts[3] == "--password":
                    username = parts[2]
                    password = parts[4]
                    
                    user = usecases.register_user(username, password)
                    print(f" Пользователь '{user.username}' зарегистрирован (id={user.user_id}). Войдите: login --username {user.username} --password ****")
                else:
                    print(" Используйте: register --username NAME --password PASS")
                    
            except Exception as e:
                print(f" Ошибка: {e}")
        
        # Команда login
        elif command.startswith("login"):
            try:
                parts = command.split()
                if len(parts) == 5 and parts[1] == "--username" and parts[3] == "--password":
                    username = parts[2]
                    password = parts[4]
                    
                    user = usecases.login_user(username, password)
                    print(f" Вы вошли как '{user.username}'")
                else:
                    print(" Используйте: login --username NAME --password PASS")
                    
            except Exception as e:
                print(f" Ошибка: {e}")
                
        elif command == "exit":
            break
        else:
            print(f"Команда '{command}' пока не реализована")