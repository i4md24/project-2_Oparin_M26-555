"""Вспомогательные функции primitive_db: работа с файлами."""

import json
from pathlib import Path


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