import json
import random

class Controller:

    # Format:
    # pool = {
    #     cost: [{
    #         championInfo,
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

    # Format:
    # odds = {
    #     level: {
    #         cost: percentage
    #     }
    # }
    odds = {}

    def getShop(self, level):
        oddsByCost = self.odds[level]
        choices = []
        for cost in range(1, 6):
            odd = oddsByCost[cost]/100
            for champion in self.pool[cost]:
                choices += [champion["championInfo"]["name"]]*int(champion["ammount"]*odd)
        shop = []
        for i in range(5):
            shop.append(random.choices(choices)[0])
        return shop

    def refreshShop(self, oldShop, level):
        # TODO - Re-add oldShop champions to ammount
        self.getShop(level)

    def __init__(self, database):

        poolSize = {}
        for key, value in database.pool.items():
            poolSize[int(key)] = value

        for champion in database.champions:
            self.pool[champion["cost"]].append({
                "championInfo": champion,
                "ammount": poolSize[champion["cost"]],
                "maxAmmount": poolSize[champion["cost"]],
            })

        for level, oddsByCost in database.odds.items():
            tempOdds = {}
            for cost, odd in oddsByCost.items():
                tempOdds[int(cost)] = odd
            self.odds[int(level)] = tempOdds
