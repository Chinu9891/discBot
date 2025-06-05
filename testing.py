import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests

url = f'https://api.twitch.tv/helix/eventsub/subscriptions'
headers = {
    'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
    'Authorization': os.getenv('TWITCH_AUTH')
}

response = requests.get(url,headers=headers)
data = response.json()
print(data)



#for x in range(2):
 #   print(url+'?id='+data['data'][x]['id'])
    #requests.delete(url+'?id='+data['data'][x]['id'],headers=headers)
