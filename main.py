import websocket
import json
import threading
import time
import hmac
import hashlib
import requests
from websocket_server import WebsocketServer
import logging

class MexcWebsocketClient:
    def __init__(self, api_key, secret_key, server_host='localhost', server_port=8000):
        self.api_key = api_key
        self.secret_key = secret_key
        self.listen_key = None
        self.ws = None
        self.keep_running = True
        self.base_url = "https://api.mexc.com"
        self.balances = {}
        self.price_changes = {}
        self.tracked_symbols = set()
        self.balances = None


        self.server = WebsocketServer(host=server_host, port=server_port, loglevel=logging.INFO)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        
        self.connected_clients = set()

        

    def generate_signature(self, query_string):
        signature = hmac.new(self.secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def get_listen_key(self):
        endpoint = "/api/v3/userDataStream"
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.generate_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        response = requests.post(url, headers={"X-MEXC-APIKEY": self.api_key})
        if response.status_code == 200:
            return response.json().get('listenKey')
        else:
            raise Exception(f"Failed to get listen key: {response.text}")
    
    def get_current_price(self):
        endpoint = "/api/v3/ticker/price"
        response = requests.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()
    
    def get_account_information(self):
        endpoint = "/api/v3/account"
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self.generate_signature(query_string)
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        response = requests.get(url, headers={"X-MEXC-APIKEY": self.api_key})
        response.raise_for_status()
        return response.json()
    
    def send_ping(self):
        if self.ws:
            try:
                ping_message = {
                    "method": "PING"
                }
                self.ws.send(json.dumps(ping_message))
                print("Sent ping message")
            except Exception as e:
                print(f"Error sending ping: {e}")
    
    def start_ping(self):
        def run():
            while self.keep_running:
                self.send_ping()
                time.sleep(20) 
        ping_thread = threading.Thread(target=run)
        ping_thread.daemon = True
        ping_thread.start()
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            print(data)
    
            account_info = self.get_account_information()
            price_data = self.get_current_price()

            price_dict = {item['symbol']: float(item['price']) for item in price_data}
            result = []
            for balance in account_info['balances']:
                asset = balance['asset']
                if float(balance['free']) == 0 and float(balance['locked']) == 0:
                    continue
                    
                if asset == 'USDT':
                    result.append({
                        'asset': asset,
                        'free': float(balance['free']),
                        'locked': float(balance['locked'])
                    })
                    continue
                
                symbol = f"{asset}USDT"
                if symbol in price_dict:
                    price = price_dict[symbol]
                    result.append({
                        'asset': asset,
                        'free': float(balance['free']) * price,
                        'locked': float(balance['locked']) * price
                    })
            self.balances = result
            self.broadcast_balances(result)

        except Exception as e:
            print(f"Error processing message: {e}")
            error_msg = json.dumps({"error": str(e)})
            self.server.send_message_to_all(error_msg)
    
    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        if self.keep_running:
            time.sleep(1)
            print("Reconnecting to MEXC WebSocket...")
            self.connect_websocket()
    
    def on_open(self, ws):
        print("WebSocket connection opened")
        self.subscribe_streams()
    
    def subscribe_streams(self):
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [
                "spot@private.account.v3.api",
                "spot@public.deals.v3.api@BTCUSDT"
            ]
        }
        self.ws.send(json.dumps(subscribe_message))
        print("Subscribed to account streams")
    
    def new_client(self, client, server):
        print(f"New client connected: {client['id']}")
        self.connected_clients.add(client['id'])
        if self.balances:
            self.broadcast_balances(self.balances)
        
    def client_left(self, client, server):
        print(f"Client disconnected: {client['id']}")
        self.connected_clients.discard(client['id'])
    
    def broadcast_balances(self, balances):
        message = json.dumps(balances)
        print(f"Broadcasting to {len(self.connected_clients)} clients")
        self.server.send_message_to_all(message)
    
    def start_server(self):
        print("Starting WebSocket server on localhost:8000")
        self.server.run_forever()
    
    def keep_alive_listen_key(self):
        while self.keep_running:
            try:
                endpoint = "/api/v3/userDataStream"
                timestamp = int(time.time() * 1000)
                query_string = f"timestamp={timestamp}&listenKey={self.listen_key}"
                signature = self.generate_signature(query_string)
                url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
                response = requests.put(url, headers={"X-MEXC-APIKEY": self.api_key})
                if response.status_code != 200:
                    print(f"Failed to keep listen key alive: {response.text}")
                else:
                    print("Successfully kept listen key alive")
                time.sleep(30 * 60)  
            except Exception as e:
                print(f"Error refreshing listen key: {e}")
                time.sleep(60)  

    def connect_websocket(self):
        self.listen_key = self.get_listen_key()
        websocket_url = f"wss://wbs.mexc.com/ws?listenKey={self.listen_key}"
        
        self.ws = websocket.WebSocketApp(
            websocket_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

        wst = threading.Thread(target=self.ws.run_forever, kwargs={'ping_interval': 30})
        wst.daemon = True
        wst.start()
        self.start_ping()

        print("Connecting to MEXC WebSocket...")
    
    def connect(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True
        server_thread.start()
        
        self.connect_websocket()
        keep_alive_thread = threading.Thread(target=self.keep_alive_listen_key)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()
    
    def close(self):
        self.keep_running = False
        if self.ws:
            self.ws.close()
        self.server.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    client = MexcWebsocketClient(
        api_key="YourApiKey",
        secret_key="YourSecretKey"
    )
    try:
        client.connect()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.close()
        print("WebSocket client stopped.")
