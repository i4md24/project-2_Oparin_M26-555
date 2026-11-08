"""Игровой цикл primitive_db: разбор и диспетчеризация команд."""

import shlex

from prompt import string

from primitive_db.constants import (
    CMD_CREATE_TABLE,
    CMD_DROP_TABLE,
    CMD_EXIT,
    CMD_HELP,
    CMD_LIST_TABLES,
    META_PATH,
)
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def print_help() -> None:
    """Вывести справку по командам работы с таблицами."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("create_table <имя_таблицы> <столбец:тип> ... - создать таблицу")
    print("drop_table <имя_таблицы> - удалить таблицу")
    print("list_tables - показать список таблиц")
    print("\nОбщие команды:")
    print("exit - выйти из программы")
    print("help - справочная информация")


def run() -> None:
    """Запустить цикл обработки команд управления таблицами."""
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
        elif command == CMD_HELP:
            print_help()
        elif command == CMD_EXIT:
            break
        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")