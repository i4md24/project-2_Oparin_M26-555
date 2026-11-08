"""Разбор сложных команд primitive_db: values, where, set.

Функции принимают список токенов команды (результат shlex.split),
проверяют формат и возвращают аргументы для функций ядра либо None
с печатью подсказки об использовании.
"""


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


def parse_insert_query(parts: list[str]) -> tuple[str, list[str]] | None:
    """Разобрать "insert into <таблица> values (<значения>)".

    Возвращает (таблица, список значений) либо None при неверном формате.
    """
    if not (len(parts) >= 5 and parts[1] == "into" and parts[3] == "values"):
        print("Использование: insert into <таблица> values (<значение>, ...)")
        return None
    values = parse_insert_values(" ".join(parts[4:]))
    if values is None:
        return None
    return parts[2], values


def parse_select_query(parts: list[str]) -> tuple[str, tuple[str, str] | None] | None:
    """Разобрать "select from <таблица> [where <столбец> = <значение>]".

    Возвращает (таблица, условие where) либо None при неверном формате.
    """
    if len(parts) == 3 and parts[1] == "from":
        return parts[2], None
    if (
        len(parts) == 7
        and parts[1] == "from"
        and parts[3] == "where"
        and parts[5] == "="
    ):
        return parts[2], (parts[4], parts[6])
    print("Использование: select from <таблица> [where <столбец> = <значение>]")
    return None


def parse_update_query(
    parts: list[str],
) -> tuple[str, str, str, tuple[str, str]] | None:
    """Разобрать "update <таблица> set <столбец> = <значение> where ...".

    Возвращает (таблица, столбец, значение, условие where) либо None.
    """
    if (
        len(parts) == 10
        and parts[2] == "set"
        and parts[4] == "="
        and parts[6] == "where"
        and parts[8] == "="
    ):
        return parts[1], parts[3], parts[5], (parts[7], parts[9])
    print(
        "Использование: update <таблица> set <столбец> = <значение> "
        "where <столбец> = <значение>"
    )
    return None


def parse_delete_query(parts: list[str]) -> tuple[str, tuple[str, str]] | None:
    """Разобрать "delete from <таблица> where <столбец> = <значение>".

    Возвращает (таблица, условие where) либо None при неверном формате.
    """
    if (
        len(parts) == 7
        and parts[1] == "from"
        and parts[3] == "where"
        and parts[5] == "="
    ):
        return parts[2], (parts[4], parts[6])
    print("Использование: delete from <таблица> where <столбец> = <значение>")
    return None