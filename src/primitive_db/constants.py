"""Константы primitive_db: пути, типы данных и имена команд."""

from pathlib import Path

# Файл с метаданными таблиц (лежит в рабочей директории)
META_PATH = Path("db_meta.json")

# Типы данных, поддерживаемые столбцами таблиц
VALID_TYPES = ("int", "str", "bool")

# Имена команд игрового цикла
CMD_CREATE_TABLE = "create_table"
CMD_DROP_TABLE = "drop_table"
CMD_LIST_TABLES = "list_tables"
CMD_HELP = "help"
CMD_EXIT = "exit"