import requests
import json

response = requests.get('https://api.polygon.io/v3/reference/options/contracts/O:SPY220909P00365000?apiKey=1XA_Gopp8G197T6HFpMDhxUIOqw8ABbb')
options = response.json()
print(json.dumps(options, indent=4, sort_keys=False))