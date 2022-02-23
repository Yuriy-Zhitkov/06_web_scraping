# Необходимо собрать информацию о вакансиях на вводимую должность (используем input) с сайтов Superjob(необязательно)
# и HH(обязательно). Приложение должно анализировать несколько страниц сайта (также вводим через input).
# Получившийся список должен содержать в себе минимум:
#
# 1) Наименование вакансии.
# 2) Предлагаемую зарплату (отдельно минимальную и максимальную; дополнительно - собрать валюту; можно использовать
#    regexp или if'ы).
# 3) Ссылку на саму вакансию.
# 4) Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Сохраните результат в json-файл

import json
import time
from pprint import pprint

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
        vac_for_search = self.vacansy.replace(" ", "+")
        # url = f'https://spb.hh.ru/search/vacancy?' \
        #       f'clusters=true&area=2&' \
        #       f'ored_clusters=true&enable_snippets=true&salary=&' \
        #       f'text={vac_for_search}&from=suggest_post&page={page_number}&' \
        #       f'hhtmFrom=vacancy_search_list'
        url = (
            f"https://spb.hh.ru/search/vacancy?"
            f"text={vac_for_search}&page={page_number}&items_on_page=20"
        )
        return url

    def gen_info(self):
        """
        Сбор информаци по запросу
        :return:
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
                        "salary_mim": f'{salary["salary_min"]}',
                        "salary_max": f'{salary["salary_max"]}',
                        "salary_curr": f'{salary["salary_curr"]}',
                        "link": f"{vacansy_title[1]}",
                    }
        return result

    def page_content(self, page_num, status_code=False):
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
        # vacansy_title = block.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
        vacansy = block.find("a", attrs={"data-qa": "vacancy-serp__vacancy-title"})
        title = vacansy.text
        link = vacansy["href"]
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
        salary = {"salary_min": "", "salary_max": "", "salary_curr": ""}
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
                salary["salary_min"] = salary_block[1]
            elif "до" in salary_block:
                salary["salary_max"] = salary_block[1]
            else:
                salary["salary_min"] = salary_block[0]
                salary["salary_max"] = salary_block[1]
        return salary


# Запуск программы
vacansy = input("Введите название вакансии: ")
count = int(input("Введите количество страниц для поиска: "))
hh_vac_01 = HHScraper(vacansy, count).gen_info()

# Сохранение результата запроса №1 в файл json
file_name = "HHScraper_result.json"
with open(file_name, "w") as f:
    json.dump(hh_vac_01, f, indent=4, ensure_ascii=False)

print("-" * 50)
print("Завершено")
