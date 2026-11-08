"""Ядро primitive_db: операции над таблицами и их данными."""

from prettytable import PrettyTable

from primitive_db.constants import META_PATH, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


@handle_db_errors
def create_table(table_name: str, columns: list[str]) -> None:
    """Создать таблицу в метаданных.

    Сама загружает и сохраняет метаданные, автоматически добавляет
    столбец ID:int в начало, проверяет, не существует ли уже такая
    таблица, и корректность типов столбцов.
    """
    metadata = load_metadata(META_PATH)
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return
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
            return
        parsed[name] = col_type
    full_columns = {"ID": "int", **parsed}
    metadata[table_name] = {"columns": full_columns}
    save_metadata(META_PATH, metadata)
    cols_str = ", ".join(
        f"{name}:{col_type}" for name, col_type in full_columns.items()
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')


@handle_db_errors
@confirm_action("удалить таблицу")
def drop_table(table_name: str) -> None:
    """Удалить таблицу из метаданных.

    Перед удалением запрашивает подтверждение (confirm_action).
    Сама загружает и сохраняет метаданные, проверяет,
    что таблица существует.
    """
    metadata = load_metadata(META_PATH)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    del metadata[table_name]
    save_metadata(META_PATH, metadata)
    print(f'Таблица "{table_name}" успешно удалена.')


@handle_db_errors
def list_tables() -> None:
    """Вывести имена всех таблиц, каждую на отдельной строке."""
    metadata = load_metadata(META_PATH)
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


@handle_db_errors
def insert(table_name: str, raw_values: list[str]) -> bool:
    """Добавить строку в таблицу.

    Сама загружает метаданные и данные таблицы, проверяет число и
    корректность значений, генерирует ID (максимум существующих + 1)
    и сохраняет файл. Возвращает True, если строка добавлена,
    иначе False.
    """
    metadata = load_metadata(META_PATH)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    columns = metadata[table_name]["columns"]
    target = [name for name in columns if name != "ID"]
    if len(raw_values) != len(target):
        print(
            f'Ошибка: неверное число значений для таблицы "{table_name}": '
            f"ожидалось {len(target)}, получено {len(raw_values)}."
        )
        return False
    values = []
    for name, raw in zip(target, raw_values):
        value = parse_value(raw, columns[name])
        if value is None:
            print(
                f'Ошибка: значение "{raw}" для столбца "{name}" '
                f"не приводится к типу {columns[name]}."
            )
            return False
        values.append(value)
    table_data = load_table_data(table_name)
    new_id = max((int(key) for key in table_data), default=0) + 1
    table_data[str(new_id)] = dict(zip(target, values))
    save_table_data(table_name, table_data)
    print(f'Строка с ID = {new_id} успешно добавлена в таблицу "{table_name}".')
    return True


@handle_db_errors
def select(
    table_name: str,
    where: tuple[str, str] | None = None,
) -> PrettyTable | None:
    """Собрать PrettyTable со строками таблицы.

    Сама загружает метаданные и данные таблицы. Если задан where
    (столбец, значение), в таблицу попадают только подходящие строки.
    Возвращает PrettyTable или None, если данные вывести нельзя;
    печатью занимается engine — так результат потом можно кэшировать.
    """
    metadata = load_metadata(META_PATH)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    columns = metadata[table_name]["columns"]
    if where is not None:
        col, raw = where
        if col not in columns:
            print(f'Ошибка: Столбца "{col}" в таблице "{table_name}" нет.')
            return None
        expected = parse_value(raw, columns[col])
        if expected is None:
            print(
                f'Ошибка: значение "{raw}" для столбца "{col}" '
                f"не приводится к типу {columns[col]}."
            )
            return None
    table_data = load_table_data(table_name)
    table = PrettyTable()
    table.field_names = list(columns)
    for key in sorted(table_data, key=int):
        row = {"ID": int(key), **table_data[key]}
        if where is None or row[col] == expected:
            table.add_row([row[name] for name in columns])
    return table


@handle_db_errors
def update(
    table_name: str,
    set_col: str,
    raw_value: str,
    where: tuple[str, str],
) -> bool:
    """Обновить значение столбца в строках, подходящих под условие.

    Сама загружает и сохраняет данные, проверяет столбцы и типы
    значений. Возвращает True, если изменения сохранены, иначе False.
    """
    metadata = load_metadata(META_PATH)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    columns = metadata[table_name]["columns"]
    if set_col not in columns:
        print(f'Ошибка: Столбца "{set_col}" в таблице "{table_name}" нет.')
        return False
    if set_col == "ID":
        print('Ошибка: Столбец "ID" изменять нельзя, он генерируется сам.')
        return False
    where_col, where_raw = where
    if where_col not in columns:
        print(f'Ошибка: Столбца "{where_col}" в таблице "{table_name}" нет.')
        return False
    value = parse_value(raw_value, columns[set_col])
    if value is None:
        print(
            f'Ошибка: значение "{raw_value}" для столбца "{set_col}" '
            f"не приводится к типу {columns[set_col]}."
        )
        return False
    expected = parse_value(where_raw, columns[where_col])
    if expected is None:
        print(
            f'Ошибка: значение "{where_raw}" для столбца "{where_col}" '
            f"не приводится к типу {columns[where_col]}."
        )
        return False
    table_data = load_table_data(table_name)
    updated = 0
    for key in sorted(table_data, key=int):
        row = {"ID": int(key), **table_data[key]}
        if row[where_col] == expected:
            table_data[key][set_col] = value
            updated += 1
    if not updated:
        print("Подходящих строк не найдено.")
        return False
    save_table_data(table_name, table_data)
    print(f"Обновлено строк: {updated}.")
    return True


@handle_db_errors
@confirm_action("удалить строки")
def delete(table_name: str, where: tuple[str, str]) -> bool:
    """Удалить строки, подходящие под условие.

    Перед удалением запрашивает подтверждение (confirm_action).
    Сама загружает и сохраняет данные, проверяет столбец условия
    и тип значения. Возвращает True, если изменения сохранены,
    иначе False.
    """
    metadata = load_metadata(META_PATH)
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    columns = metadata[table_name]["columns"]
    where_col, where_raw = where
    if where_col not in columns:
        print(f'Ошибка: Столбца "{where_col}" в таблице "{table_name}" нет.')
        return False
    expected = parse_value(where_raw, columns[where_col])
    if expected is None:
        print(
            f'Ошибка: значение "{where_raw}" для столбца "{where_col}" '
            f"не приводится к типу {columns[where_col]}."
        )
        return False
    table_data = load_table_data(table_name)
    deleted = 0
    for key in sorted(table_data, key=int):
        row = {"ID": int(key), **table_data[key]}
        if row[where_col] == expected:
            del table_data[key]
            deleted += 1
    if not deleted:
        print("Подходящих строк не найдено.")
        return False
    save_table_data(table_name, table_data)
    print(f"Удалено строк: {deleted}.")
    return True