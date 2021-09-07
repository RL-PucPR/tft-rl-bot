import json


def request():
    import requests

    r = requests.get('http://raw.communitydragon.org/latest/cdragon/tft/en_us.json')

    with open("resources/en_us_.json", "w") as f:
        json.dump(r.json(), f)


def required_exp():
    data = {}
    with open("resources/base_values.json", "r") as f:
        for lvl, required in json.load(f)["requiredExp"].items():
            data[int(lvl)] = required
    return data


class DDragon:
    champions = []
    championPrices = {}
    items = []
    pool = {}
    odds = {}
    rewardValues = {}
    REJECTED = -50

    def load(self):
        # Gets latest set
        with open("resources/en_us_.json", "r") as f:
            data = json.load(f)
        set_name = ""
        latest_set = {"champions": []}
        for s in data["setData"]:
            if set_name < s["mutator"]:
                latest_set = s
                set_name = s["mutator"]

        for champion in latest_set["champions"]:
            self.champions.append({
                "name": champion["name"],
                "cost": champion["cost"],
                "stats": champion["stats"],
                "traits": champion["traits"],
                "ability": champion["ability"],
            })
            self.championPrices[champion["name"]] = champion["cost"]

        with open("resources/base_values.json", "r") as f:
            data = json.load(f)
            self.pool = data["pool"]
            self.odds = data["odds"]
            for lvl, required in data["requiredExp"].items():
                self.requiredExp[int(lvl)] = required
            self.rewardValues = data["rewardValues"]
        return self

    def __init__(self):
        self.requiredExp = {}
        self.load()
