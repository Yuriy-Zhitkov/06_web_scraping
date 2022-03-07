# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные
#    вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.


import json
import time
from pprint import pprint
from urllib.parse import quote_plus, urlsplit, urlunsplit

# from pymongo import MongoClient
import pymongo
import requests
from bs4 import BeautifulSoup


class HHScraper:
    def __init__(self, vacansy: str, pgs_count: int):
        """
        Создание экземпляра класса HHScrapper
        :param vacansy: Название вакансии
        """
        self.vacansy = vacansy
        self.pgs_count = pgs_count

    def re_count(self, count_of_pages: int):
        """
        Переопределение атрибута self.pgs_count
        :param count_of_pages: int Кол-во страниц с найденными вакансиями
        :return: self.pgs_count
        """
        if self.pgs_count == "all":
            self.pgs_count = int(count_of_pages)
        else:
            pass
        return self.pgs_count

    @staticmethod
    def headers():
        """
        Настройка headers для запросов на сайт HH
        :return: str: Настройка User-Agent
        """
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/15.3 Safari/605.1.15"
        }

    def url_hh(self, page_number):
        """
        Формирование адреса для запроса поиска вакансий на сайт HH
        :return: str: Адрес запроса
        """
        vac_for_search = quote_plus(self.vacansy)
        url = (
            f"https://spb.hh.ru/search/vacancy?"
            f"text={vac_for_search}&page={page_number}&items_on_page=20"
        )
        return url

    def gen_info(self):
        """
        Сбор информаци по запросу
        :return: словарь, содержащий ключ - "страница.номер_вакансии",
                                     значение - словарь с параметрами (название ваканчии, зарплата и т.д)
        """
        print(f'{"-" * 50}\nПоиск информаци о вакансии: {self.vacansy}')
        page_content = self.page_content(page_num=0, status_code=True)
        count_of_pages = self.count_of_pages(page_content)
        print(f"{count_of_pages[1]}.\nВакансии размещены на {count_of_pages[0]} стр.")
        result = {}
        for page_num in range(count_of_pages[0]):
            if page_num == self.pgs_count:
                break
            else:
                print(f'{"-" * 50}\nПереход на страницу {page_num + 1}')
                page_content = self.page_content(page_num=page_num, status_code=True)
                vacansy_blocks_list = self.vacansy_blocks(page_content)
                for i, block in enumerate(vacansy_blocks_list):
                    vacansy_title = self.vacansy_title(block)
                    salary = self.salary(block)
                    result[f"{page_num + 1}.{i + 1}"] = {
                        "vacansy_title": f"{vacansy_title[0]}",
                        "salary_min": salary["salary_min"],
                        "salary_max": salary["salary_max"],
                        "salary_curr": salary["salary_curr"],
                        "link": f"{vacansy_title[1]}",
                    }

        return result

    def page_content(self, page_num, status_code=False):
        """

        :param page_num:
        :param status_code:
        :return:
        """
        sleep = 2
        time.sleep(sleep)
        print(f"Ожидание {sleep} сек.")
        response = requests.get(
            self.url_hh(page_number=page_num), headers=self.headers()
        )  # отправка запроса на сайт HH.ru
        print(f"Код запроса: {response.status_code}") if status_code else None
        page_content = BeautifulSoup(response.text, "html.parser")
        return page_content

    @staticmethod
    def count_of_pages(page_content):
        """
        Поиск кол-ва страниц и вакансий
        :param page_content: объект bs4.BeautifulSoup
        :return: tuple Кортеж со значениями кол-ва страниц с вакансиями и общим кол-вом найденных вакансий
        """
        count_pgs = int(
            page_content.findAll("a", attrs={"data-qa": "pager-page"})[-1].text
        )
        count_vac = page_content.find("h1", attrs={"data-qa": "bloko-header-3"}).text
        return count_pgs, count_vac

    @staticmethod
    def vacansy_blocks(page_content):
        """
        Поиск блоков с информацией о вакансиях на странице
        :param page_content: объект bs4.BeautifulSoup
        :return: list Список объектов, содержащих информацию о вакансиях
        """
        vacansy_block_list = page_content.findAll(
            "div", attrs={"class": "vacancy-serp-item vacancy-serp-item_redesigned"}
        )
        return vacansy_block_list

    @staticmethod
    def vacansy_title(block):
        """
        Поиск названия вакансии
        :param block: объект bs4.BeautifulSoup
        :return: str Название вакансии
        """
        vacansy = block.find("a", attrs={"data-qa": "vacancy-serp__vacancy-title"})
        title = vacansy.text
        # link = vacansy["href"]

        url_split = list(urlsplit(vacansy["href"]))
        url_split[3:4] = [""]
        link = urlunsplit(url_split)

        # return title, link
        return title, link

    @staticmethod
    def salary(block):
        """
        Поиск значения заработной платы
        :param block: объект bs4.BeautifulSoup
        :return: dict Словарь со значениями заработной платы: salary_min - минимальная, salary_max - максимальная, salary_cur - валюта
        """
        salary_block = block.find(
            "span", attrs={"data-qa": "vacancy-serp__vacancy-compensation"}
        )
        salary = {"salary_min": None, "salary_max": None, "salary_curr": None}
        if salary_block == None:
            pass
        else:
            salary_block = (
                str(salary_block.text)
                .replace("\u202f", "")
                .replace(" – ", " ")
                .replace(".", "")
                .rsplit()
            )
            salary["salary_curr"] = salary_block[-1]
            if "от" in salary_block:
                salary["salary_min"] = int(salary_block[1])
            elif "до" in salary_block:
                salary["salary_max"] = int(salary_block[1])
            else:
                salary["salary_min"] = int(salary_block[0])
                salary["salary_max"] = int(salary_block[1])
        return salary


# TODO: превратить параметры в словарь и использовать для настройки класса/функции
# MONGO_HOST = "localhost"
# MONGO_PORT = 27017
# MONGO_DB = "vac_db"
# MONGO_COLLECTION = "hh_vac"


# создание документов и отправка в базу данных
class hh_db:
    def __init__(self, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION):
        self.MONGO_HOST = MONGO_HOST
        self.MONGO_PORT = MONGO_PORT
        self.MONGO_DB = MONGO_DB
        self.MONGO_COLLECTION = MONGO_COLLECTION

    @staticmethod
    def print_mongo_docs(cursor):
        for doc in cursor:
            pprint(doc)

    # запись информации о вакансииях в базу данных
    def document_insert(self, vac_info: dict, upsert=True):
        with pymongo.MongoClient(self.MONGO_HOST, self.MONGO_PORT) as client:
            db = client[self.MONGO_DB]
            collections = db[self.MONGO_COLLECTION]
            count_before = collections.count_documents({})
            if upsert == True:
                for i, key in enumerate(vac_info.keys()):
                    collections.update_one(
                        {"link": vac_info[f"{key}"].pop("link")},
                        {"$set": vac_info[f"{key}"]},
                        upsert=True,
                    )
                    count = i + 1
            else:
                for i, key in enumerate(vac_info.keys()):
                    collections.insert_one(vac_info[f"{key}"])
            count_after = collections.count_documents({}) - count_before
            print(
                f'{"-" * 50}\nВ базу данных {self.MONGO_DB}.{self.MONGO_COLLECTION} '
                f"добавлены документы в кол-ве: {count_after} шт"
            )

    # Запрос на вывод результатов из базы данных
    def find_vac_salary(self, gt_salary: int, salary_curr: str, show_vac=True):
        with pymongo.MongoClient(self.MONGO_HOST, self.MONGO_PORT) as client:
            db = client[self.MONGO_DB]
            collections = db[self.MONGO_COLLECTION]
            filter = {"salary_min": {"$gt": gt_salary}, "salary_curr": salary_curr}
            cursor = collections.find(filter)
            count_doc = collections.count_documents(filter)
            print(
                f'{"-" * 50}\nИнформация о вакансиях по параметрам:\n'
                f"- заработная плата от {gt_salary}\n"
                f"- количество найденных вакансий {count_doc}"
            )
            self.print_mongo_docs(cursor) if show_vac else None


# Запуск программы
vacansy = input("Введите название вакансии: ")
count = int(input("Введите количество страниц для поиска: "))

# Создаем объект HHScrapper и применяем метод gen_info() для сбора информации о вакансиях
hh_vac_01 = HHScraper(vacansy, count).gen_info()

# Создаем объект hh_db и отправляем новую информацию методом document_insert() в базу данных MongoDB
db_hh_vac_01 = hh_db(
    "localhost", 27017, MONGO_DB="db_hh_vac", MONGO_COLLECTION="data_scientist"
)
db_hh_vac_01.document_insert(hh_vac_01)

# Запрос на фильтрацию вакансий и вывод результата из базы данных
db_hh_vac_01.find_vac_salary(gt_salary=30000, salary_curr="руб", show_vac=True)

print("-" * 50)
print("Завершено")
