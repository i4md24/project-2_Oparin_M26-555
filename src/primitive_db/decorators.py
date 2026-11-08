"""Декораторы primitive_db: обработка ошибок, подтверждения, время."""

import functools


def handle_db_errors(func):
    """Перехватывать исключения функции и печатать понятные сообщения.

    Вместо падения программы выводит диагностическое сообщение
    и возвращает None.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name: str):
    """Фабрика декораторов: спросить подтверждение перед действием.

    Принимает название действия (например, «удалить таблицу») и
    возвращает декоратор, который перед вызовом функции задаёт
    вопрос да/нет. При отказе функция не вызывается.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f"Вы уверены, что хотите {action_name}? (да/нет): ")
            if answer.strip().lower() in ("да", "y", "yes"):
                return func(*args, **kwargs)
            print("Действие отменено.")
            return None

        return wrapper

    return decorator