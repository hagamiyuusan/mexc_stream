import websocket
import json
import threading
import time
from utils import get_listen_key
import hmac
import hashlib
import requests
import asyncio


class MexcWebsocketClient:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.listen_key = None
        self.ws = None
        self.keep_running = True
        self.base_url = "https://api.mexc.com"
        self.balances = {}  
        self.price_changes = {} 
        self.tracked_symbols = set()  

    def generate_signature(self, query_string):
        signature = hmac.new(self.secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        return signature
    

    def on_ping(self, ws, message):
        ws.send(b'', websocket.ABNF.OPCODE_PONG)
        self.last_ping = time.time()
        print("Received ping, sent pong")

    def get_listen_key(self):
        endpoint = "/api/v3/userDataStream"
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.generate_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        return url

    def get_current_price(self):
        print("Getting current price")
        endpoint = "/api/v3/ticker/price"
        response = requests.get(f"{self.base_url}{endpoint}")
        return response.json()

    def get_account_information(self):
        print("Getting account information")
        endpoint = "/api/v3/account"
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.generate_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        response = requests.get(url, headers={"X-MEXC-APIKEY": self.api_key})
        return response.json()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            print(f"Received message: {message}")
            if isinstance(data, dict):
                if "ping" in data:
                    pong_msg = json.dumps({"pong": data["ping"]})
                    ws.send(pong_msg)
                    print("Sent application-level pong response")
                    return

            # Xử lý Ping message
            if "ping" in data:
                pong_msg = json.dumps({"pong": data["ping"]})
                ws.send(pong_msg)
                print("Sent pong response")
                return

            account_info = self.get_account_information()
            all_price = self.get_current_price()

            print(account_info)
            print(all_price)
            

            
            print(f"Received message: {message}")
        except Exception as e:
            print(f"Error processing message: {e}")


    def subscribe_streams(self):
        # Đăng ký stream account private
        subscribe_message = {
            "method": "SUBSCRIPTION",
            "params": [
                "spot@private.account.v3.api",
            ]
        }
        self.ws.send(json.dumps(subscribe_message))
        print("Subscribed to account stream")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection opened")
        self.subscribe_streams()


    def keep_alive_listen_key(self):
        while self.keep_running:
            try:
                self.listen_key = get_listen_key(self.api_key, self.secret_key)
                print(f"Listen key refreshed: {self.listen_key}")
                time.sleep(30 * 60) 
            except Exception as e:
                print(f"Error refreshing listen key: {e}")

    def connect(self):
        self.listen_key = get_listen_key(self.api_key, self.secret_key)
        websocket_url = f"wss://wbs.mexc.com/ws?listenKey={self.listen_key}"
        
        websocket.enableTrace(True)  
        self.ws = websocket.WebSocketApp(
            websocket_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            on_ping=self.on_ping,
        )

        keep_alive_thread = threading.Thread(target=self.keep_alive_listen_key)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

        self.ws.run_forever(ping_interval=30)  

    def close(self):
        self.keep_running = False
        if self.ws:
            self.ws.close()