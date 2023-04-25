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
