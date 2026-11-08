"""Константы primitive_db: пути, типы данных и имена команд."""

# Файл с метаданными таблиц (лежит в рабочей директории)
META_PATH = "db_meta.json"

# Директория с файлами данных таблиц (data/<имя>.json)
DATA_DIR = "data"

# Типы данных, поддерживаемые столбцами таблиц
VALID_TYPES = ("int", "str", "bool")

# Имена команд игрового цикла
CMD_CREATE_TABLE = "create_table"
CMD_DROP_TABLE = "drop_table"
CMD_LIST_TABLES = "list_tables"
CMD_HELP = "help"
CMD_EXIT = "exit"

# Имена команд работы с данными (CRUD)
CMD_INSERT = "insert"
CMD_SELECT = "select"
CMD_UPDATE = "update"
CMD_DELETE = "delete"
CMD_INFO = "info"