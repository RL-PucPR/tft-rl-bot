import json

class Controller:

    # Format:
    # pool = {
    #     cost: [{
    #         champion,
    #         ammount,
    #         maxAmmount
    #     }]
    # }
    pool = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }

    def __init__(self, database):

        with open("resources/base_values.json", "r") as f:
            poolSizeJson = json.load(f)["pool"]

        poolSize = {}
        for key, value in poolSizeJson.items():
            poolSize[int(key)] = value

        for champion in database.champions:
            self.pool[champion["cost"]].append({
                "champion": champion,
                "ammount": poolSize[champion["cost"]],
                "maxAmmount": poolSize[champion["cost"]],
            })
