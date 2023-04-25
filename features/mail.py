import os
from dotenv import load_dotenv
from selenium import webdriver  # https://chromedriver.chromium.org/downloads
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time
import re

load_dotenv()

login = os.getenv('LOGIN')
pwd = os.getenv('PASSWORD')
url = 'https://account.mail.ru/login/'

# Запускаем браузер
chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(
    executable_path='./chromedriver.exe',
    options=chrome_options)

# переходим на страницу логина
driver.get(url)

# Вводим логин
login_field = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.NAME,'username'))
)
login_field.send_keys(login)
login_field.submit()

# Вводим пароль
password_field = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.NAME,'password'))
)
password_field.send_keys(pwd)
password_field.submit()

# Вычисляем сколько писем в ящике
inbox_element = WebDriverWait(driver, 60).until(
    EC.visibility_of_element_located((By.CLASS_NAME,'nav__item_active'))
)
title = inbox_element.get_attribute('title')
regex = r"Входящие, (\d*) "
count_emails = int(re.search(regex, title).group(1))
print(f"Всего писем: {count_emails}")

# Собираем список ссылок на письма
urls_marker = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CLASS_NAME,'js-letter-list-item'))
)
url_list = driver.find_elements_by_class_name('js-letter-list-item')
url_set = set()

for a in url_list:
    url_set.add(a.get_attribute('href'))  # собираем ссылки, пока они видны на экране

while len(url_set) != count_emails:
    actions = ActionChains(driver)
    actions.move_to_element(url_list[-1])
    actions.perform()
    time.sleep(1)
    url_list = driver.find_elements_by_class_name('js-letter-list-item')
    for a in url_list:
        url_set.add(a.get_attribute('href'))  # собираем ссылки, пока они видны на экране
    print(f"Собрано URL'ов: {len(url_set)}")

# Открываем каждое письмо и парсим содержимое
emails = []
for a in url_set:
    driver.get(a)
    letter_author_wrapper = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter__author'))
    )
    email = {
        'letter_author': letter_author_wrapper.find_element_by_class_name('letter-contact').get_attribute('title'),
        'letter_date': letter_author_wrapper.find_element_by_class_name('letter__date').text,
        'letter_title': driver.find_element_by_class_name('thread__subject').text,
        'letter_body': driver.find_element_by_class_name('letter-body').text
    }
    emails.append(email)
    print(f"Обработана ссылка: {a}")

# Сохраняем в БД
client = MongoClient('mongodb://localhost:27017/')
db = client['emails']
collection_name = 'mail_db'
db.inbox.insert_many(emails)

print('FINISH')
