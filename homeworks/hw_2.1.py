'''
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы) с сайтов Superjob и HH.
Приложение должно анализировать несколько страниц сайта
(также вводим через input или аргументы). Получившийся список должен содержать
в себе минимум:
- Наименование вакансии.
- Предлагаемую зарплату (отдельно минимальную и максимальную).
- Ссылку на саму вакансию.
- Сайт, откуда собрана вакансия.

По желанию можно добавить ещё параметры вакансии (
например, работодателя и расположение). Структура должна быть одинаковая
для вакансий с обоих сайтов. Общий результат можно вывести
с помощью dataFrame через pandas.

Можно выполнить по желанию один любой вариант
или оба при желании и возможности.
'''

import requests
import pandas as pd

pd.set_option("display.max_rows", None,
              "display.max_columns", None,
              "display.width", 1000)


def search_similar_vacancies(vacancy_name):
    url = "https://api.hh.ru/vacancies"

    params = {
        "text": vacancy_name,
        "search_field": "name",
        "per_page": 100
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      "AppleWebKit/537.36 (KHTML, like Gecko)"
                      "Chrome/112.0.0.0 Safari/537.36",
        "HH-User-Agent": "HH.ru",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.ok:
        vacancy_data = []
        vacancies = response.json()['items']

        for i in vacancies:
            vacancy_data.append({
                "vacancy_name": i['name'],
                "company_name": i['employer']['name'],
                "city": i['area']['name'],
                "salary_min": i['salary']['from'] if i['salary'] else None,
                "salary_max": i['salary']['to'] if i['salary'] else None,
                "salary_currency": i['salary']['currency'] if i['salary'] else None,
                # "vacancy_link": i['apply_alternate_url'],
                "site": "hh.ru"
            })

        df = pd.DataFrame(vacancy_data)
        return df

    else:
        print("Ошибка: не удалось получить вакансии")
        return None


vacancy_name = input("Введите название вакансии для поиска: ")
df = search_similar_vacancies(vacancy_name)

if df is not None:
    print(df)
