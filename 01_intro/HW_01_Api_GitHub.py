# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json; написать функцию, возвращающую(return) список репозиториев.

# Дополнительная информация:
# https://pyneng.github.io/pyneng-3/GitHub-API-JSON-example/
# https://chel-center.ru/python-yfc/2020/11/17/kak-ispolzovat-api-github/

import json
import os
from pprint import pprint

import requests
from dotenv import load_dotenv

# Подключение приватных данных
load_dotenv("./.env")  # take environment variables from .env.
name = os.getenv("name_github", None)  # получение логина
token = os.getenv("token_github", None)  # получение токена


# Общие настройки
username = "Yuriy-Zhitkov"  # интересующий пользователь в запросе
# username = "nizhikebinesi"  # интересующий пользователь в запросе


# Формирование адреса запроса
url_01 = f"https://api.github.com/users/{username}/repos"  # адрес обращения №1


# Отправка запроса
response_01 = requests.get(
    url_01, auth=(name, token)
)  # запрос №1 для получения информаци
data_01 = response_01.json()


# Сохранение результата запроса №1 в файл json
file_name = "response_01_result.json"
with open(file_name, "w") as f:
    json.dump(data_01, f, indent=4)


# Вывод информации запроса №1
# pprint(data_01)
print(f"\nАдрес запроса {url_01}\nСтатус обращения: код {response_01.status_code}")
# Вывод списка репозиториев
print(f"\nСписок репозиториев пользователя {username}:")
for i in range(len(data_01)):
    print(
        f'Репозиторий #{i+1}: {data_01[i]["html_url"]}. Описание: {data_01[i]["description"]}'
    )
