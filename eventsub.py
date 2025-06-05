import os
import json
import threading
import requests
from dotenv import load_dotenv
from websocket import WebSocketApp
from shared import set_status

load_dotenv()

class EventSubClient:
    """
    Manages a single WebSocket session and multiple subscriptions
    """
    def __init__(self, broadcaster_ids):
        self.broadcaster_ids = list(set(broadcaster_ids))  # Ensure unique IDs
        self.ws = None
        self.session_id = None

    def on_open(self, ws):
        print("WebSocket connection opened")

    def on_message(self, ws, message):
        print(f"Received message: {message}")
        data = json.loads(message)
        msg_type = data['metadata']['message_type']

        if msg_type == 'session_keepalive':
            print("Keepalive ping, id:", data['metadata']['message_id'])

        elif msg_type == 'session_welcome':
            self.session_id = data['payload']['session']['id']
            print('Session id is:', self.session_id)
            self._create_subscriptions(self.session_id)

        elif msg_type == 'notification':
            print('Notification received')
            set_status(True)

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed:", close_status_code, close_msg)

    def _create_subscriptions(self, session_id, new_ids=None):
        """
        Create EventSub subscriptions for broadcaster IDs
        """
        # Determine which IDs to subscribe
        ids_to_sub = new_ids or self.broadcaster_ids
        headers = {
            'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
            'Authorization': os.getenv('TWITCH_AUTH'),
            'Content-Type': 'application/json'
        }
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

        for broadcaster_id in ids_to_sub:
            payload = {
                'type': 'stream.online',
                'version': '1',
                'condition': {'broadcaster_user_id': broadcaster_id},
                'transport': {'method': 'websocket', 'session_id': session_id}
            }
            resp = requests.post(url, headers=headers, json=payload)
            try:
                print(f"Subscription for {broadcaster_id}: {resp.json()}")
            except ValueError:
                print(f"Failed to parse response for {broadcaster_id}, status code {resp.status_code}")

    def start(self):
        """
        Initialize and run the WebSocketApp; only one session will run at a time
        """
        if self.ws:
            print("WebSocket is already running.")
            return
        self.ws = WebSocketApp(
            "wss://eventsub.wss.twitch.tv/ws",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        # Run in current thread (or call from a separate thread if needed)
        self.ws.run_forever()

    def subscribe_new(self, broadcaster_ids):
        """
        Subscribe to additional broadcaster IDs without reopening the socket
        """
        if not self.session_id:
            print("Session not established yet; cannot subscribe new IDs.")
            return
        new_ids = [bid for bid in broadcaster_ids if bid not in self.broadcaster_ids]
        if not new_ids:
            print("No new broadcaster IDs to subscribe.")
            return
        self.broadcaster_ids.extend(new_ids)
        self._create_subscriptions(self.session_id, new_ids=new_ids)

# Global client control
_client = None
_thread = None

def start_websocket(broadcaster_ids):
    """
    Start EventSubClient in a background thread. Pass a single ID or a list.
    """
    global _client, _thread
    ids = broadcaster_ids if isinstance(broadcaster_ids, list) else [broadcaster_ids]
    if _client is None:
        _client = EventSubClient(ids)
        _thread = threading.Thread(target=_client.start, daemon=True)
        _thread.start()
    else:
        _client.subscribe_new(ids)


def close_websocket():
    """
    Close the WebSocket session and stop the client
    """
    global _client, _thread
    if _client and _client.ws:
        _client.ws.close()
    _client = None
    _thread = None

# Usage in responses.py:
# from eventsub import start_websocket, close_websocket
# start_websocket(['123', '456'])  # pass list or single ID
# close_websocket()
