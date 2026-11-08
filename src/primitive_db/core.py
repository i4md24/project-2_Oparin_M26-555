"""Ядро primitive_db: логика управления таблицами."""

from primitive_db.constants import VALID_TYPES


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict | None:
    """Создать таблицу в метаданных.

    Автоматически добавляет столбец ID:int в начало, проверяет,
    не существует ли таблица, и корректность типов столбцов.
    Возвращает обновлённые метаданные или None при ошибке.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    parsed: dict[str, str] = {}
    for token in columns:
        name, sep, col_type = token.partition(":")
        if (
            not sep
            or not name
            or name in parsed
            or name == "ID"
            or col_type not in VALID_TYPES
        ):
            print(f"Некорректное значение: {token}. Попробуйте снова.")
            return None
        parsed[name] = col_type
    full_columns = {"ID": "int", **parsed}
    metadata[table_name] = {"columns": full_columns}
    cols_str = ", ".join(
        f"{name}:{col_type}" for name, col_type in full_columns.items()
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict | None:
    """Удалить таблицу из метаданных.

    Проверяет, что таблица существует, и удаляет её из словаря.
    Возвращает обновлённые метаданные или None при ошибке.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> None:
    """Вывести имена всех таблиц, каждую на отдельной строке."""
    for name in metadata:
        print(f"- {name}")


def parse_value(raw: str, col_type: str) -> int | bool | str | None:
    """Привести строковое значение к типу столбца.

    Возвращает приведённое значение или None, если привести не удалось.
    """
    if col_type == "int":
        try:
            return int(raw)
        except ValueError:
            return None
    if col_type == "bool":
        lowered = raw.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        return None
    return raw


def insert(
    metadata: dict,
    table_data: dict,
    table_name: str,
    raw_values: list[str],
) -> dict | None:
    """Добавить строку в таблицу.

    Проверяет существование таблицы, число и корректность значений,
    сама генерирует ID (максимум существующих + 1). Возвращает
    обновлённые данные таблицы или None при ошибке.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    columns = metadata[table_name]["columns"]
    target = [name for name in columns if name != "ID"]
    if len(raw_values) != len(target):
        print(
            f'Ошибка: неверное число значений для таблицы "{table_name}": '
            f"ожидалось {len(target)}, получено {len(raw_values)}."
        )
        return None
    values = []
    for name, raw in zip(target, raw_values):
        value = parse_value(raw, columns[name])
        if value is None:
            print(
                f'Ошибка: значение "{raw}" для столбца "{name}" '
                f"не приводится к типу {columns[name]}."
            )
            return None
        values.append(value)
    new_id = max((int(key) for key in table_data), default=0) + 1
    table_data[str(new_id)] = dict(zip(target, values))
    print(f'Строка с ID = {new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data