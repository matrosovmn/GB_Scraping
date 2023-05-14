from pymongo import MongoClient


class BookscraperPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client['labirint_ru']
        self.collection = self.mongobase['books']

    def process_item(self, item, spider):
        item['price'] = float(item['price']) if item['price'] else 0
        item['discount_price'] = float(item['discount_price']) if item['discount_price'] else 0
        item['rating'] = float(item['rating']) if item['rating'] else 0

        self.collection.insert_one(dict(item))

        return item
