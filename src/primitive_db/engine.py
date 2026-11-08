"""Игровой цикл primitive_db: разбор и диспетчеризация команд."""

import shlex

from prompt import string

from primitive_db.constants import (
    CMD_CREATE_TABLE,
    CMD_DROP_TABLE,
    CMD_EXIT,
    CMD_HELP,
    CMD_INSERT,
    CMD_LIST_TABLES,
    CMD_SELECT,
    CMD_UPDATE,
    META_PATH,
)
from primitive_db.core import (
    create_table,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Вывести справку по всем командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("create_table <имя_таблицы> <столбец:тип> ... - создать таблицу")
    print("drop_table <имя_таблицы> - удалить таблицу")
    print("list_tables - показать список таблиц")
    print("\n***Процесс работы с данными***")
    print("insert into <имя_таблицы> values (<значение>, ...) - добавить строку")
    print("select from <имя_таблицы> [where <столбец> = <значение>] - показать строки")
    print("update <таблица> set <столбец> = <значение> where ... - изменить строки")
    print("\nОбщие команды:")
    print("exit - выйти из программы")
    print("help - справочная информация")


def parse_insert_values(raw: str) -> list[str] | None:
    """Разобрать строку "(Sergei, 28, true)" в список значений.

    Возвращает список строк-значений или None при ошибке формата.
    """
    raw = raw.strip()
    if not raw.startswith("(") or not raw.endswith(")"):
        print("Значения нужно указать в круглых скобках: values (<значение>, ...)")
        return None
    inner = raw[1:-1].strip()
    if not inner:
        return []
    return [token.strip() for token in inner.split(",")]


def run() -> None:
    """Запустить цикл обработки команд."""
    print_help()
    while True:
        metadata = load_metadata(META_PATH)
        parts = shlex.split(string("Введите команду: "))
        if not parts:
            continue
        command, *args = parts
        if command == CMD_CREATE_TABLE:
            if not args:
                print("Использование: create_table <имя_таблицы> <столбец:тип> ...")
            else:
                result = create_table(metadata, args[0], args[1:])
                if result is not None:
                    save_metadata(META_PATH, result)
        elif command == CMD_DROP_TABLE:
            if not args:
                print("Использование: drop_table <имя_таблицы>")
            else:
                result = drop_table(metadata, args[0])
                if result is not None:
                    save_metadata(META_PATH, result)
        elif command == CMD_LIST_TABLES:
            list_tables(metadata)
        elif command == CMD_INSERT:
            if len(parts) >= 5 and parts[1] == "into" and parts[3] == "values":
                values = parse_insert_values(" ".join(parts[4:]))
                if values is not None:
                    table_data = load_table_data(parts[2])
                    result = insert(metadata, table_data, parts[2], values)
                    if result is not None:
                        save_table_data(parts[2], result)
            else:
                print("Использование: insert into <таблица> values (<значение>, ...)")
        elif command == CMD_SELECT:
            if len(parts) == 3 and parts[1] == "from":
                select(metadata, load_table_data(parts[2]), parts[2])
            elif (
                len(parts) == 7
                and parts[1] == "from"
                and parts[3] == "where"
                and parts[5] == "="
            ):
                where = (parts[4], parts[6])
                select(metadata, load_table_data(parts[2]), parts[2], where)
            else:
                print(
                    "Использование: select from <таблица> "
                    "[where <столбец> = <значение>]"
                )
        elif command == CMD_UPDATE:
            if (
                len(parts) == 10
                and parts[2] == "set"
                and parts[4] == "="
                and parts[6] == "where"
                and parts[8] == "="
            ):
                result = update(
                    metadata,
                    load_table_data(parts[1]),
                    parts[1],
                    parts[3],
                    parts[5],
                    (parts[7], parts[9]),
                )
                if result is not None:
                    save_table_data(parts[1], result)
            else:
                print(
                    "Использование: update <таблица> set <столбец> = <значение> "
                    "where <столбец> = <значение>"
                )
        elif command == CMD_HELP:
            print_help()
        elif command == CMD_EXIT:
            break
        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")