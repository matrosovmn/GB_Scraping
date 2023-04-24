'''
1. Написать приложение, которое собирает основные новости с сайта на выбор
   news.mail.ru, lenta.ru, yandex-новости.
   Для парсинга использовать XPath. Структура данных должна содержать:
        название источника;
        наименование новости;
        ссылку на новость;
        дата публикации.
2. Сложить собранные данные в БД
'''

from pymongo import MongoClient, InsertOne
from lxml import html
import requests


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

    # Если коллекция уже существует, удаляем ее
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

    # Вставляем данные в базу данных
    collection = db[collection_name]
    bulk_write = [InsertOne(item) for item in data]
    collection.bulk_write(bulk_write)

    # Выводим количество записей в базе данных
    print(f"{collection.count_documents({})} записей в базе данных.")


if __name__ == '__main__':
    write_to_db()
