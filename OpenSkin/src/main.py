import requests
from models import json_to_skin, to_avro_skin

URL = "https://api.openskin.dev/v1/prices"
skin_name = "AK-47 | Crane Flight (Field-Tested)"

# tester - laver en request
response = requests.get(URL, params={"item": skin_name})

response_json = response.json()
skin = json_to_skin(response_json)

skin_data = to_avro_skin(skin)

print("Skin data:", skin_data)
