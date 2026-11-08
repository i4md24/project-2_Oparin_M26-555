"""Игровой цикл primitive_db: разбор и диспетчеризация команд."""

import shlex

from prompt import string

from primitive_db.constants import (
    CMD_CREATE_TABLE,
    CMD_DELETE,
    CMD_DROP_TABLE,
    CMD_EXIT,
    CMD_HELP,
    CMD_INSERT,
    CMD_LIST_TABLES,
    CMD_SELECT,
    CMD_UPDATE,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import (
    parse_delete_query,
    parse_insert_query,
    parse_select_query,
    parse_update_query,
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
    print("delete from <имя_таблицы> where <столбец> = <значение> - удалить строки")
    print("\nОбщие команды:")
    print("exit - выйти из программы")
    print("help - справочная информация")


def run() -> None:
    """Запустить цикл обработки команд.

    Движок разбивает ввод на токены (shlex), разбор сложных команд
    выполняет parser, а вызов функций ядра остаётся здесь; вся работа
    с файлами и перехват ошибок живут в core. Результаты select
    кэшируются замыканием create_cacher; после любой команды, меняющей
    данные, кэш пересоздаётся, чтобы не показывать устаревшие строки.
    """
    print_help()
    cached_select = create_cacher()
    while True:
        parts = shlex.split(string("Введите команду: "))
        if not parts:
            continue
        command, *args = parts
        if command == CMD_CREATE_TABLE:
            if not args:
                print("Использование: create_table <имя_таблицы> <столбец:тип> ...")
            else:
                create_table(args[0], args[1:])
                cached_select = create_cacher()
        elif command == CMD_DROP_TABLE:
            if not args:
                print("Использование: drop_table <имя_таблицы>")
            else:
                drop_table(args[0])
                cached_select = create_cacher()
        elif command == CMD_LIST_TABLES:
            list_tables()
        elif command == CMD_INSERT:
            parsed = parse_insert_query(parts)
            if parsed is not None:
                table, values = parsed
                insert(table, values)
                cached_select = create_cacher()
        elif command == CMD_SELECT:
            parsed = parse_select_query(parts)
            if parsed is not None:
                table, where = parsed
                result = cached_select((table, where), lambda: select(table, where))
                if result is not None:
                    print(result)
        elif command == CMD_UPDATE:
            parsed = parse_update_query(parts)
            if parsed is not None:
                table, set_col, raw_value, where = parsed
                update(table, set_col, raw_value, where)
                cached_select = create_cacher()
        elif command == CMD_DELETE:
            parsed = parse_delete_query(parts)
            if parsed is not None:
                table, where = parsed
                delete(table, where)
                cached_select = create_cacher()
        elif command == CMD_HELP:
            print_help()
        elif command == CMD_EXIT:
            break
        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")