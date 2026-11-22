import requests
from models import json_to_skin

URL = "https://api.openskin.dev/v1/prices"

def get_skins(skin_names):
    skins = []

    for skin_name in skin_names:
        response = requests.get(URL, params={"item": skin_name})
        response.raise_for_status()

        #json format
        response_json = response.json()
        skin = json_to_skin(response_json)
        skins.append(skin)

    return skins
    

