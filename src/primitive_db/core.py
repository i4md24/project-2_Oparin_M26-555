"""Ядро primitive_db: логика управления таблицами."""

from prettytable import PrettyTable

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


def select(
    metadata: dict,
    table_data: dict,
    table_name: str,
    where: tuple[str, str] | None = None,
) -> None:
    """Вывести строки таблицы в виде таблицы PrettyTable.

    Если задан where (столбец, значение), вывести только строки,
    у которых значение столбца совпадает с указанным.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    columns = metadata[table_name]["columns"]
    if where is not None:
        col, raw = where
        if col not in columns:
            print(f'Ошибка: Столбца "{col}" в таблице "{table_name}" нет.')
            return
        expected = parse_value(raw, columns[col])
        if expected is None:
            print(
                f'Ошибка: значение "{raw}" для столбца "{col}" '
                f"не приводится к типу {columns[col]}."
            )
            return
    table = PrettyTable()
    table.field_names = list(columns)
    for key in sorted(table_data, key=int):
        row = {"ID": int(key), **table_data[key]}
        if where is None or row[col] == expected:
            table.add_row([row[name] for name in columns])
    print(table)


def update(
    metadata: dict,
    table_data: dict,
    table_name: str,
    set_col: str,
    raw_value: str,
    where: tuple[str, str],
) -> dict | None:
    """Обновить значение столбца в строках, подходящих под условие.

    Проверяет таблицу, столбцы и типы значений. Возвращает
    обновлённые данные таблицы или None, если менять нечего.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    columns = metadata[table_name]["columns"]
    if set_col not in columns:
        print(f'Ошибка: Столбца "{set_col}" в таблице "{table_name}" нет.')
        return None
    if set_col == "ID":
        print('Ошибка: Столбец "ID" изменять нельзя, он генерируется сам.')
        return None
    where_col, where_raw = where
    if where_col not in columns:
        print(f'Ошибка: Столбца "{where_col}" в таблице "{table_name}" нет.')
        return None
    value = parse_value(raw_value, columns[set_col])
    if value is None:
        print(
            f'Ошибка: значение "{raw_value}" для столбца "{set_col}" '
            f"не приводится к типу {columns[set_col]}."
        )
        return None
    expected = parse_value(where_raw, columns[where_col])
    if expected is None:
        print(
            f'Ошибка: значение "{where_raw}" для столбца "{where_col}" '
            f"не приводится к типу {columns[where_col]}."
        )
        return None
    updated = 0
    for key in sorted(table_data, key=int):
        row = {"ID": int(key), **table_data[key]}
        if row[where_col] == expected:
            table_data[key][set_col] = value
            updated += 1
    if not updated:
        print("Подходящих строк не найдено.")
        return None
    print(f"Обновлено строк: {updated}.")
    return table_data


def delete(
    metadata: dict,
    table_data: dict,
    table_name: str,
    where: tuple[str, str],
) -> dict | None:
    """Удалить строки, подходящие под условие.

    Проверяет таблицу, столбец условия и тип значения. Возвращает
    обновлённые данные таблицы или None, если удалять нечего.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    columns = metadata[table_name]["columns"]
    where_col, where_raw = where
    if where_col not in columns:
        print(f'Ошибка: Столбца "{where_col}" в таблице "{table_name}" нет.')
        return None
    expected = parse_value(where_raw, columns[where_col])
    if expected is None:
        print(
            f'Ошибка: значение "{where_raw}" для столбца "{where_col}" '
            f"не приводится к типу {columns[where_col]}."
        )
        return None
    deleted = 0
    for key in sorted(table_data, key=int):
        row = {"ID": int(key), **table_data[key]}
        if row[where_col] == expected:
            del table_data[key]
            deleted += 1
    if not deleted:
        print("Подходящих строк не найдено.")
        return None
    print(f"Удалено строк: {deleted}.")
    return table_data