import requests

URL = "https://api.openskin.dev/v1/prices"
skin_name = "AK-47 | Redline (Field-Tested)"

# tester - laver en request
response = requests.get(URL, params={"item": skin_name})

response_json = response.json()

print(response_json)
