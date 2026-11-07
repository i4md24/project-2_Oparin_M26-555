"""Движок primitive_db: приветствие, справка и парсинг команд."""

from prompt import string


def show_help() -> None:
    """Вывести справку по доступным командам."""
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome() -> None:
    """Показать приветствие и в цикле обрабатывать команды пользователя."""
    print("***")
    show_help()
    while True:
        command = string("Введите команду: ").strip()
        if command == "exit":
            break
        if command == "help":
            show_help()