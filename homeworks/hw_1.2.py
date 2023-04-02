'''
    2. Изучить список открытых API
    (https://www.programmableweb.com/category/all/apis).
    Найти среди них любое, требующее авторизацию (любого типа).
    Выполнить запросы к нему, пройдя авторизацию.
    Ответ сервера записать в файл.
    Если нет желания заморачиваться с поиском,
    возьмите API вконтакте (https://vk.com/dev/first_guide).
    Сделайте запрос, чтобы получить список всех сообществ
    на которые вы подписаны.
'''

import requests
import json

user_id = 743784474
auth_url = f'https://oauth.vk.com/authorize?client_id={user_id}&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1'

print(f'Перейдите по ссылке:\n{auth_url}\nи получите токен доступа.')
access_token = input('\nВведите токен доступа: ')

response = requests.get(
    f'https://api.vk.com/method/groups.get?extended=1&access_token={access_token}&v=5.131').json()

print('\nСписок сообществ, на которые вы подписаны')
for group in response['response']['items']:
    print(f"{group['name']}")

# with open('task02_response.json', 'w') as file:
    #json.dump(response, file)