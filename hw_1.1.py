'''
1. Посмотреть документацию к API GitHub,
разобраться как вывести список репозиториев
для конкретного пользователя, сохранить JSON-вывод в файле *.json.
'''

import requests
import json

url = 'https://api.github.com'
user = input('Введите логин пользователя Github: ').strip()
params = {'per_page': 200}

response = requests.get(f'{url}/users/{user}/repos', params=params).json()

print(f'\nСписок репозиториев пользователя {user}: ')
for i in response:
    print(f"{i['name']} - {i['description']}")

with open('task01_response.json', 'w') as outfile:
    json.dump(response, outfile)
