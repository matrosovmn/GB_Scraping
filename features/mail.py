import os
import time
import re
from dotenv import load_dotenv
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

load_dotenv()

login = os.getenv('LOGIN')
pwd = os.getenv('PASSWORD')
url = 'https://account.mail.ru/login/'

chrome_driver_path = './chromedriver.exe'

# Запускаем браузер
chrome_options = Options()
chrome_options.add_argument('--start-fullscreen')
service = Service(executable_path=chrome_driver_path, options=chrome_options)
driver = webdriver.Chrome(service=service)
driver.maximize_window()


# переходим на страницу логина
driver.get(url)

# Вводим логин
login_field = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.NAME, 'username')))
login_field.send_keys(login)
login_field.submit()

# Вводим пароль
password_field = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.NAME, 'password')))
password_field.send_keys(pwd)
password_field.submit()

# Вычисляем сколько писем в ящике
inbox_element = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Inbox')]"))
)
title = inbox_element.get_attribute('title')
regex = r"Входящие, (\d*) "
count_emails = int(re.search(regex, title).group(1))
print(f"Всего писем: {count_emails}")

# Собираем список ссылок на письма
url_list = []
url_set = set()

while len(url_set) != count_emails:
    try:
        url_list = driver.find_elements_by_class_name('js-letter-list-item')
        for a in url_list:
            url_set.add(a.get_attribute('href'))  # собираем ссылки, пока они видны на экране
        actions = ActionChains(driver)
        actions.move_to_element(url_list[-1])
        actions.perform()
        time.sleep(1)
        print(f"Собрано URL'ов: {len(url_set)}")
    except (TimeoutException, NoSuchElementException):
        print("Ошибка при сборе списка ссылок на письма")
        break

# Открываем каждое письмо и парсим содержимое
emails = []
for a in url_set:
    try:
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
    except TimeoutException:
        print(f"Не удалось обработать ссылку: {a}. Тайм-аут ожидания элемента.")
    except Exception as e:
        print(f"Не удалось обработать ссылку: {a}. Произошла ошибка: {e}")

# Сохраняем в БД
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emails']
    collection_name = 'mail_db'
    db.inbox.insert_many(emails)
    print('Данные сохранены в базу данных.')
except Exception as e:
    print(f"Ошибка при сохранении данных в базу данных: {e}")
finally:
    driver.quit()
    print('Браузер закрыт.')
