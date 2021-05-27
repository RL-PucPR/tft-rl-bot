import random
from database import DDragon


class Controller:
    # Format:
    # pool = {
    #     cost: [{
    #         championInfo,
    #         amount,
    #         maxAmount
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

    def changePoolAmount(self, shop, func):
        for cost, championsByCost in self.pool.items():
            for i in range(len(championsByCost)):
                self.pool[cost][i]["amount"] = func(championsByCost[i]["amount"],
                                                    shop.count(championsByCost[i]["championInfo"]["name"]))

    def generateShop(self, level):
        oddsByCost = self.odds[level]
        choices = []
        for cost in range(1, 6):
            odd = oddsByCost[cost] / 100
            for champion in self.pool[cost]:
                choices += [champion["championInfo"]["name"]] * int(champion["amount"] * odd)
        shop = []
        for i in range(5):
            if len(choices) > 0:
                shop.append(random.choices(choices)[0])
            else:
                shop.append(None)
        self.changePoolAmount(shop, lambda a, b: a - b)
        return shop

    def refreshShop(self, oldShop, level):
        self.changePoolAmount(oldShop, lambda a, b: a + b)
        return self.generateShop(level)

    def __init__(self, load=False):

        database = DDragon()

        if load:
            database.request()
            database.load()

        poolSize = {}
        for key, value in database.pool.items():
            poolSize[int(key)] = value

        for champion in database.champions:
            if champion["cost"] > 5:
                continue
            if len(champion["traits"]) > 0 and champion["cost"] <= 5:
                self.pool[champion["cost"]].append({
                    "championInfo": champion,
                    "amount": poolSize[champion["cost"]],
                    "maxAmount": poolSize[champion["cost"]],
                })
            else:
                self.pool[champion["cost"]].append({
                    "championInfo": champion,
                    "amount": 0,
                    "maxAmount": 0,
                })

        for level, oddsByCost in database.odds.items():
            tempOdds = {}
            for cost, odd in oddsByCost.items():
                tempOdds[int(cost)] = odd
            self.odds[int(level)] = tempOdds
