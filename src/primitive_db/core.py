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