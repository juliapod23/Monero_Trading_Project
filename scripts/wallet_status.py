import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:18083/json_rpc")

def get_wallet_balance():
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "get_balance",
    }
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post(RPC_URL, json = payload, headers = headers)
        return response.json()
    except Exception as e:
        print("Error:", e)
        
if __name__ == "__main__":
    print(get_wallet_balance)