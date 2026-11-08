"""Замыкание primitive_db: кэширование результатов select."""


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