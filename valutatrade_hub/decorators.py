from valutatrade_hub.logging_config import logger


def log_action(action="", verbose=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = "OK"
                user_id = args[0] if len(args) > 0 else "unknown"
                currency = args[1] if len(args) > 1 else ""
                amount = args[2] if len(args) > 2 else 0

                # Выполняем функцию
                func_result = func(*args, **kwargs)

                # Формируем лог
                log_msg = (
                    f"{action} user='{user_id}' currency='{currency}' amount={amount}"
                )
                if verbose and isinstance(func_result, dict):
                    if "rate" in func_result:
                        log_msg += f" rate={func_result['rate']} base='USD'"

                logger.info(log_msg)
                return func_result

            except Exception as e:
                result = "ERROR"
                user_id = args[0] if len(args) > 0 else "unknown"
                logger.error(
                    f"{action} user='{user_id}' result={result} "
                    f"error_type={type(e).__name__} "
                    f"error_message='{str(e)}'"
                )
                raise

        return wrapper

    return decorator
