import socketio
import random
import time
import tkinter as tk
import threading
import uuid
import requests

# Constants
SERVER_URL = 'https://webservice-0-2.onrender.com'
NAMESPACE = '/ccdev'
# Global variables
running = False
running_lock = threading.Lock()

sio = socketio.Client()

def get_access_token(username, password):
    auth_url = f"https://webservice-0-2.onrender.com/api/login"  # Update with your authentication endpoint
    credentials = {"username": username, "password": password}
    response = requests.post(auth_url, json=credentials)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        if access_token:
            return access_token
    return None

def connect_to_server():
    try:
        # Get access token
        username = "bob"
        password = "bobpass"
        auth_token = get_access_token(username, password)
        
        if auth_token:
            headers = {'Authorization':  f'{auth_token}'}
            sio.connect(SERVER_URL, namespaces=[NAMESPACE], transports=['websocket'], headers=headers)
            print(username," is connected to server")
            return True
        else:
            print("Failed to obtain access token")
            return False

    except socketio.exceptions.ConnectionError as e:
        print(f"Failed to connect: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

@sio.event(namespace=NAMESPACE)
def connect():
    print('Connected to server')
    sio.emit('join', namespace=NAMESPACE)

@sio.event(namespace=NAMESPACE)
def disconnect():
    print('Disconnected from server')

@sio.event(namespace=NAMESPACE)
def connection_success(data):
    print('Connection successful:', data)

@sio.event(namespace=NAMESPACE)
def data_inserted(data):
    print('New Item Inserted', data)

def generate_random_data():
    sysUUID = str(uuid.uuid4())
    lastrowid = random.randint(1, 1000)
    sid = random.randint(1, 1000)
    score = random.randint(0, 10)
    timestamp = int(time.time())
    duration = random.randint(1, 100)
    ts = random.randint(1, 100)

    json_data = {
        "sysUUID": sysUUID,
        "lastrowid": lastrowid,
        "sid": sid,
        "score": score,
        "timestamp": timestamp,
        "duration": duration,
        "ts": ts
    }

    sio.emit('data_received', {'data': json_data}, namespace=NAMESPACE)
    print(f"Sent data to room: {json_data}")

def start_sending_data():
    global running
    with running_lock:
        running = True
    while running:
        generate_random_data()
        time.sleep(10)

def stop_sending_data():
    global running
    with running_lock:
        running = False
    enable_start_button()

def disable_start_button():
    start_button.config(state=tk.DISABLED)

def enable_start_button():
    start_button.config(state=tk.NORMAL)

def start_button_clicked():
    disable_start_button()
    threading.Thread(target=start_sending_data).start()

root = tk.Tk()
root.title("bob client")
root.geometry("250x100")  # Set the window size

start_button = tk.Button(root, text="Start Sending Data", command=start_button_clicked)
start_button.pack()

stop_button = tk.Button(root, text="Stop Sending Data", command=stop_sending_data)
stop_button.pack()

# Connect to server when the application starts
connect_to_server()

root.mainloop()
