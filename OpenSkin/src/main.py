from openskin import get_skins
from models import to_avro_skin

skin_names = [
    "AK-47 | Crane Flight (Field-Tested)",
    "Glock-18 | Umbral Rabbit (Factory New)"
]

skins = get_skins(skin_names)
skins_data = [to_avro_skin(skin) for skin in skins]

print("Number of skins retrieved:", len(skins_data))


for skin in skins_data:
    print("Skin:" + skin["item"])
    print("Lowest Ask:", skin["lowest_ask"])
