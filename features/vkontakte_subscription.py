import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

user_id = os.getenv('USER_ID')
auth_url = f'https://oauth.vk.com/authorize?client_id={user_id}&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1'

print(f'Перейдите по ссылке:\n{auth_url}\nи получите токен доступа.')
access_token = input('\nВведите токен доступа: ')

response = requests.get(
    f'https://api.vk.com/method/groups.get?extended=1&access_token={access_token}&v=5.131').json()

print('\nСписок сообществ, на которые вы подписаны')
for group in response['response']['items']:
    print(f"{group['name']}")

# with open('subscription_response.json', 'w') as file:
    # json.dump(response, file)
