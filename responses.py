from random import randint, choice
import requests
import threading
import time
import os
import websocket
import json


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()
    
    if lowered == '':
        return 'Shush'
    if user_input[0] == '$':
        streamer_login = user_input[1:]
        url = f'https://api.twitch.tv/helix/streams?user_login={streamer_login}'
        headers = {
            'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
            'Authorization': os.getenv('TWITCH_AUTH')
        }
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return data['data'][0]['game_name']
            else:
                return 'Streamer not live right now!'
        else:
            print(f"Failed to get user data: {response.status_code} - {response.text}")
            return 'Error!'
        