import requests

def get_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"
    resp = requests.get(url)
    return resp.json()

print(get_price())