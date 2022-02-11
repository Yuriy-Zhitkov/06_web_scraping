# Зарегистрироваться на https://openweathermap.org/api и написать функцию,которая получает погоду в данный момент
# для города, название которого получается через input. https://openweathermap.org/current/


import os
from pprint import pprint

import requests
from dotenv import load_dotenv

# Подключение приватных данных
load_dotenv("./.env")  # take environment variables from .env.
user_name = os.getenv("name_weather", None)  # получение логина
API_key = os.getenv("token_weather", None)  # получение токена


# Настройки
city = str(input("Введите название города в России: "))
country_code = 643  # код страны, см. ISO 3166


# Формирование адреса запроса
url_01 = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit={1}&appid={API_key}"

# Отправка запроса
response_01 = requests.get(url_01)
direct = response_01.json()
# pprint(direct)
print("")

lat = float(direct[0]["lat"])  # широта
lon = float(direct[0]["lon"])  # долгота

url_02 = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}"
response_02 = requests.get(url_02)
weather = response_02.json()
# pprint(weather)
temp = float(weather["main"]["temp"] - 273.15)  # температура в градусах Цельсия
pressure = int(weather["main"]["pressure"])  # давление в мм.рт.ст


Current_weather = (
    f'\nГород: {direct[0]["local_names"]["ru"]} ({direct[0]["country"]})'
    f"\nТекущая температура {round(temp, 2)} град. цельсия"
    f"\nДавление {pressure} мм.рт.ст."
)

print(Current_weather)

# print(response_01.status_code)

print()
