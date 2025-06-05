import os
import requests
import asyncio
from discord import Message
from shared import get_status, set_status
from eventsub import start_websocket, close_websocket

headers = {
    'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
    'Authorization': os.getenv('TWITCH_AUTH')
}

async def get_response(user_input: str, message: Message):
    lowered = user_input.lower()

    if lowered == '':
        return 'Shush'

    if user_input.startswith("$$"):
        streamer_login = user_input[2:]
        broadcaster_id = get_broadcaster_id(streamer_login)
        if broadcaster_id == 'error':
            await message.channel.send('❌ Error: Invalid broadcaster name or API failure.')
            return
        start_websocket(broadcaster_id)
        await message.channel.send(f'✅ Subscribed to {streamer_login}. Type `$close_socket` to unsubscribe.')

        # Start polling loop for notifications
        await twitch_notification_loop(message)

    elif user_input == '$hello':
        await message.channel.send('Hi there! 👋')

    elif user_input == '$close_socket':
        unsubscribe_all()
        close_websocket()
        await message.channel.send('✅ WebSocket closed and all subscriptions removed.')

def get_broadcaster_id(login_name: str) -> str:
    url = f'https://api.twitch.tv/helix/users?login={login_name}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]['id']
        else:
            return 'error'
    else:
        print(f"Failed to get user data: {response.status_code} - {response.text}")
        return 'error'

async def twitch_notification_loop(message: Message):
    """Periodically checks if streamer went live and notifies."""
    while True:
        if get_status():
            await message.channel.send(f'{message.author.mention} 🚨 Your followed streamer is live!')
            set_status(False)
        await asyncio.sleep(2)

def unsubscribe_all():
    """Utility to unsubscribe from all Twitch subscriptions."""
    url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
    resp = requests.get(url, headers=headers)
    try:
        data = resp.json().get('data', [])
        for sub in data:
            sub_id = sub['id']
            requests.delete(f'{url}?id={sub_id}', headers=headers)
            print(f"Unsubscribed from: {sub_id}")
    except Exception as e:
        print(f"Error during unsubscribe: {e}")
