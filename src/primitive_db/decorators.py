"""Декораторы и замыкание primitive_db: ошибки, подтверждения, время, кэш."""

import functools
import time


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


def log_time(func):
    """Замерять и печатать время выполнения функции.

    Берёт time.monotonic до и после вызова: монотонные часы
    не зависят от перевода системного времени. Имя функции
    печатается из func.__name__ — его сохраняет functools.wraps
    даже в стеке декораторов.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнена за {elapsed:.6f} с.")
        return result

    return wrapper


def create_cacher():
    """Создать кэшер — функцию, помняющую результаты в замыкании.

    Возвращает функцию cache_result(key, value_func). Словарь cache
    живёт в замыкании: снаружи он недоступен, но сохраняется между
    вызовами cache_result. Каждый вызов create_cacher создаёт
    независимый кэш — поэтому «пересоздать кэшер» означает
    «полностью очистить кэш».
    """

    cache: dict = {}

    def cache_result(key, value_func):
        """Вернуть результат из кэша либо вычислить и запомнить его.

        Значение None (так select сообщает об ошибке) не кэшируется,
        чтобы сообщение об ошибке печаталось при каждом запросе.
        """
        if key not in cache:
            value = value_func()
            if value is not None:
                cache[key] = value
            return value
        return cache[key]

    return cache_result