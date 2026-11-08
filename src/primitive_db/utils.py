"""Вспомогательные функции primitive_db: работа с файлами."""
import json
from pathlib import Path

from primitive_db.constants import DATA_DIR


def load_metadata(filepath: Path) -> dict:
    """Загрузить метаданные таблиц из JSON-файла.

    Если файл не найден, вернуть пустой словарь.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: Path, data: dict) -> None:
    """Сохранить метаданные таблиц в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_table_data(table_name: str) -> dict:
    """Загрузить данные таблицы из файла data/<имя>.json.

    Если файл не найден (таблица ещё пуста), вернуть пустой словарь.
    """
    path = DATA_DIR / f"{table_name}.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_table_data(table_name: str, data: dict) -> None:
    """Сохранить данные таблицы в файл data/<имя>.json."""
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"{table_name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)