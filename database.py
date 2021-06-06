import json


def request():
    import requests

    r = requests.get('http://raw.communitydragon.org/latest/cdragon/tft/en_us.json')

    with open("resources/en_us_.json", "w") as f:
        json.dump(r.json(), f)


class DDragon:

    champions = []
    items = []
    pool = {}
    odds = {}

    def load(self):
        # Gets latest set
        with open("resources/en_us_.json", "r") as f:
            data = json.load(f)
        set_name = ""
        latest_set = {"champions": []}
        for set in data["setData"]:
            if set_name < set["mutator"]:
                latest_set = set
                set_name = set["mutator"]

        for champion in latest_set["champions"]:
            self.champions.append({
                "name": champion["name"],
                "cost": champion["cost"],
                "stats": champion["stats"],
                "traits": champion["traits"],
                "ability": champion["ability"],
            })

        with open("resources/base_values.json", "r") as f:
            data = json.load(f)
            self.pool = data["pool"]
            self.odds = data["odds"]

    def __init__(self):
        self.load()
