import json
import websocket
import os
import requests

username = 'zackrawrr'



def on_message(ws, message):
    print(f"Received message: {message}")
    kek = json.loads(message)
    print(kek['payload']['session']['id'])
    

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")
    # Example: Send a message when the connection is opened
    ws.send("Hello, WebSocket!")
    
ws = websocket.WebSocketApp(
    "wss://eventsub.wss.twitch.tv/ws",  # Replace with your WebSocket URL
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)



#ws.on_open = on_open
#ws.run_forever()