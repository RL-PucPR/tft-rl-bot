class DDragon:

    def __init__(self):
        import requests
        import json

        r = requests.get('http://raw.communitydragon.org/latest/cdragon/tft/en_us.json')

        with open("resources/en_us_.json", "w") as f:
            json.dump(r.json(), f)
