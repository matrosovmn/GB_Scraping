from pymongo import MongoClient
from lxml import html
import requests
from pprint import pprint


def parse_lenta():
    url = 'https://lenta.ru'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      'AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/112.0.0.0 Safari/537.36',
    }

    response = requests.get(url, headers=headers)

    dom = html.fromstring(response.text)
    news_list = dom.xpath("//a[contains(@class, '_topnews')]")

    data_list = []

    for count, article in enumerate(news_list):
        try:
            data_dict = {}

            data_dict['source'] = 'lenta.ru'
            if count == 0:

                data_dict['title'] = article.xpath(".//div/h3/text()")[0]
            else:
                data_dict['title'] = article.xpath(".//div/span/text()")[0]
            data_dict['link'] = f'{url}{article.xpath(f".//@href")[0]}'

            response = requests.get(data_dict['link'], headers=headers)
            tree = html.fromstring(response.text)
            data_dict['date'] = tree.xpath("//a[@class='topic-header__item topic-header__time']/text()")[0]

            data_list.append(data_dict)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка: {e}")
            continue
    return data_list


def write_to_db():
    data = parse_lenta()

    # Подключаемся к MongoDB и выбираем базу данных
    client = MongoClient('mongodb://localhost:27017/')
    db = client['news']
    collection_name = 'lenta_db'

    # Получаем ссылки на уже сохраненные новости
    existing_links = set()
    for document in db[collection_name].find({}, {'link': 1}):
        existing_links.add(document['link'])

    # Вставляем только новые данные в базу данных
    new_data = []
    for item in data:
        if item['link'] not in existing_links:
            new_data.append(item)
    if new_data:
        db[collection_name].insert_many(new_data)

    # Выводим количество записей в базе данных
    print(f"{db[collection_name].count_documents({})} записей в базе данных.")

    # Выводим записи в терминал из базы данных
    for document in db[collection_name].find({}, {'title': 1, 'date': 1}):
        pprint(document)


if __name__ == '__main__':
    write_to_db()
