import json


class DDragon:

    champions = []
    items = []
    pool = {}
    odds = {}

    def request(self):
        import requests

        r = requests.get('http://raw.communitydragon.org/latest/cdragon/tft/en_us.json')

        with open("resources/en_us_.json", "w") as f:
            json.dump(r.json(), f)

    def load(self):
        # Gets latest set
        with open("resources/en_us_.json", "r") as f:
            data = json.load(f)
        setName = ""
        latestSet = {"champions": []}
        for set in data["setData"]:
            if setName < set["mutator"]:
                latestSet = set
                setName = set["mutator"]

        for champion in latestSet["champions"]:
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
