import os

from dotenv import load_dotenv

# pip install python-dotenv  # установка библиотеки через терминал для работы с env файлами


load_dotenv("../.env")  # take environment variables from .env.

key = "USER_NAME"


user_name = os.getenv(key, None)  # получение ключа, способ 1
work_book = os.getenv("WORK_BOOK", None)

user_name1 = os.environ.get(key, None)  # получение ключа, способ 2
wrong_book1 = os.getenv(
    "WRONG_BOOK", False
)  # пример, если в запросе ошибочное имя переменной, которого нет в .env


print(user_name)
print(work_book)

print(user_name1)
print(wrong_book1)
