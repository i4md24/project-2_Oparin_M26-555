"""Игровой цикл primitive_db: разбор и диспетчеризация команд."""

import shlex

from prompt import string

from primitive_db.caching import create_cacher
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
    """Запустить цикл обработки команд.

    Движок только разбирает команду на части и вызывает функцию ядра;
    вся работа с файлами и перехват ошибок живут в core. Результаты
    select кэшируются замыканием create_cacher; после любой команды,
    меняющей данные, кэш пересоздаётся, чтобы не показывать
    устаревшие строки.
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
            if len(parts) >= 5 and parts[1] == "into" and parts[3] == "values":
                values = parse_insert_values(" ".join(parts[4:]))
                if values is not None:
                    insert(parts[2], values)
                    cached_select = create_cacher()
            else:
                print("Использование: insert into <таблица> values (<значение>, ...)")
        elif command == CMD_SELECT:
            if len(parts) == 3 and parts[1] == "from":
                table = cached_select((parts[2], None), lambda: select(parts[2]))
                if table is not None:
                    print(table)
            elif (
                len(parts) == 7
                and parts[1] == "from"
                and parts[3] == "where"
                and parts[5] == "="
            ):
                where = (parts[4], parts[6])
                table = cached_select(
                    (parts[2], where), lambda: select(parts[2], where)
                )
                if table is not None:
                    print(table)
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
                update(parts[1], parts[3], parts[5], (parts[7], parts[9]))
                cached_select = create_cacher()
            else:
                print(
                    "Использование: update <таблица> set <столбец> = <значение> "
                    "where <столбец> = <значение>"
                )
        elif command == CMD_DELETE:
            if (
                len(parts) == 7
                and parts[1] == "from"
                and parts[3] == "where"
                and parts[5] == "="
            ):
                delete(parts[2], (parts[4], parts[6]))
                cached_select = create_cacher()
            else:
                print(
                    "Использование: delete from <таблица> "
                    "where <столбец> = <значение>"
                )
        elif command == CMD_HELP:
            print_help()
        elif command == CMD_EXIT:
            break
        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")