from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions


client = MongoClient('mongodb://localhost:27017/')
db = client['mvideo_db']
collection = db['bestsellers']

url = 'https://www.mvideo.ru'
title_site = 'М.Видео'
chrome_driver_path = './chromedriver.exe'

chrome_options = Options()
chrome_options.add_argument('--start-fullscreen')
service = Service(executable_path=chrome_driver_path, options=chrome_options)
driver = webdriver.Chrome(service=service)
driver.maximize_window()


driver.get(url)

try:
    bestsellers = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//mvid-carousel[@class='ng-star-inserted']"))
    )
except exceptions.NoSuchElementException:
    print('Bestsellers has not been found')
    driver.quit()
    exit()

while True:
    try:
        next_button = WebDriverWait(bestsellers, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ng-star-inserted"))
        )

        driver.execute_script("$(arguments[0]).click();", next_button)
    except exceptions.TimeoutException:
        print('Сбор данных окончен')
        break

goods = bestsellers.find_elements_by_css_selector('li.gallery-list-item')

for good in goods:
    item = {}
    item['title'] = good.find_element_by_css_selector(
        'a.sel-product-tile-title') \
        .get_attribute('innerHTML')

    item['good_link'] = good.find_element_by_css_selector(
        'a.sel-product-tile-title') \
        .get_attribute('href')

    item['price'] = float(
        good.find_element_by_css_selector(
            'div.c-pdp-price__current').get_attribute('innerHTML').replace(
                '&nbsp;', '').replace('¤', ''))

    item['image_link'] = good.find_element_by_css_selector(
        'img[class="lazy product-tile-picture__image"]') \
        .get_attribute('src')

    collection.update_one({'good_link': item['good_link']}, {'$set': item},
                          upsert=True)

driver.quit()
