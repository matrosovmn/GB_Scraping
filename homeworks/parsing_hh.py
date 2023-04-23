'''
Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
и реализовать функцию, которая будет добавлять только новые
вакансии/продукты в вашу базу.
Написать функцию, которая производит поиск и выводит на экран вакансии
с заработной платой больше введённой суммы
(необходимо анализировать оба поля зарплаты).
'''

import json
import requests
from tabulate import tabulate
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


pd.set_option("display.max_rows", None,
              "display.max_columns", 9,
              "display.max_colwidth", None,
              "display.expand_frame_repr", False,
              "display.width", None)


class Vacancy:
    def __init__(self, vacancy_name, company_name, city, salary_min, salary_max, salary_currency, vacancy_link, site):
        self.name = vacancy_name
        self.company_name = company_name
        self.city = city
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.salary_currency = salary_currency
        self.vacancy_link = vacancy_link
        self.site = site

    @classmethod
    def from_hh(cls, hh_vacancy):
        vacancy_name = hh_vacancy['name']
        company_name = hh_vacancy['employer']['name']
        city = hh_vacancy['area']['name']
        salary_min = hh_vacancy['salary']['from'] if hh_vacancy['salary'] else None
        salary_max = hh_vacancy['salary']['to'] if hh_vacancy['salary'] else None
        salary_currency = hh_vacancy['salary']['currency'] if hh_vacancy['salary'] else None
        vacancy_link = hh_vacancy['apply_alternate_url']
        site = 'hh.ru'
        return cls(vacancy_name, company_name, city, salary_min, salary_max, salary_currency, vacancy_link, site)

    def to_dict(self):
        return {
            'vacancy_name': self.name,
            'company_name': self.company_name,
            'city': self.city,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'vacancy_link': self.vacancy_link,
            'site': self.site
        }


class VacancyCollection:
    def __init__(self, collection):
        self.collection = collection
        self.collection.create_index("vacancy_link", unique=True)

    def add_vacancy(self, vacancy):
        try:
            self.collection.insert_one(vacancy.to_dict())
            print("Новая вакансия добавлена в базу данных!")
        except DuplicateKeyError:
            print("Такая вакансия уже есть в базе данных!")
        except Exception as err:
            print(f'Произошла другая ошибка: {err}')

    def add_vacancies(self, vacancies):
        for vacancy in vacancies:
            self.add_vacancy(vacancy)

    def find_vacancies_with_salary_greater_than(self, min_salary):
        count = self.collection.count_documents({"$or": [
            {"salary_min": {"$gte": min_salary}},
            {"salary_max": {"$gte": min_salary}}
        ]})
        if count > 0:
            cursor = self.collection.find({"$or": [
                {"salary_min": {"$gte": min_salary}},
                {"salary_max": {"$gte": min_salary}}
            ]})
            df = pd.DataFrame(list(cursor))
            print(tabulate(df, headers='keys', tablefmt='psql'))
        else:
            print(f'Нет вакансий с зарплатой больше {min_salary}')


def search_vacancies(vacancy_name, min_salary):
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": vacancy_name,
        "search_field": "name",
        "per_page": 100,
        "salary": min_salary
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      "AppleWebKit/537.36 (KHTML, like Gecko)"
                      "Chrome/112.0.0.0 Safari/537.36",
        "HH-User-Agent": "HH.ru",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        vacancies = response.json()['items']

        vacancy_data = [Vacancy.from_hh(vacancy) for vacancy in vacancies]
        return vacancy_data

    except requests.exceptions.HTTPError as http_err:
        print(f'Произошла ошибка HTTP: {http_err.response.status_code} {http_err.response.reason}')
    except requests.exceptions.ConnectionError as conn_err:
        print(f'Произошла ошибка подключения: {conn_err}')
    except json.decoder.JSONDecodeError as json_err:
        print(f'Произошла ошибка декодирования JSON: {json_err}')
    except Exception as err:
        print(f'Произошла другая ошибка: {err}')

    return None


def main():
    vacancy_name = input("Введите название вакансии для поиска: ")
    min_salary = int(input("Введите минимальную зарплату для поиска: "))
    vacancy_data = search_vacancies(vacancy_name, min_salary)

    try:
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['vacancies']
        collection_name = 'hh_db'

        if collection_name in db.list_collection_names():
            print("Коллекция существует, добавление новых вакансий...")
            collection = db[collection_name]
        else:
            print("Создание новой коллекции...")
            collection = db.create_collection(collection_name)

        vc = VacancyCollection(collection)
        vc.add_vacancies(vacancy_data)
        vc.find_vacancies_with_salary_greater_than(min_salary)

    except Exception as e:
        print("Ошибка!: не удалось добавить данные в MongoDB")
        print(e)
    else:
        print("Данные успешно добавлены в MongoDB")


if __name__ == '__main__':
    main()
