import random
from database import DDragon

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

    def changePoolAmmount(self, shop, func):
        for cost, championsByCost in self.pool.items():
            for i in range(len(championsByCost)):
                self.pool[cost][i]["ammount"] = func(championsByCost[i]["ammount"], shop.count(championsByCost[i]["championInfo"]["name"]))

    def generateShop(self, level):
        oddsByCost = self.odds[level]
        choices = []
        for cost in range(1, 6):
            odd = oddsByCost[cost]/100
            for champion in self.pool[cost]:
                choices += [champion["championInfo"]["name"]]*int(champion["ammount"]*odd)
        shop = []
        for i in range(5):
            if len(choices) > 0:
                shop.append(random.choices(choices)[0])
            else:
                shop.append(None)
        self.changePoolAmmount(shop, lambda a, b: a-b)
        return shop

    def refreshShop(self, oldShop, level):
        self.changePoolAmmount(oldShop, lambda a, b: a+b)
        return self.generateShop(level)

    def __init__(self):
        database = DDragon()

        poolSize = {}
        for key, value in database.pool.items():
            poolSize[int(key)] = value

        for champion in database.champions:
            if len(champion["traits"]) > 0:
                self.pool[champion["cost"]].append({
                    "championInfo": champion,
                    "ammount": poolSize[champion["cost"]],
                    "maxAmmount": poolSize[champion["cost"]],
                })
            else:
                self.pool[champion["cost"]].append({
                    "championInfo": champion,
                    "ammount": 0,
                    "maxAmmount": 0,
                })

        for level, oddsByCost in database.odds.items():
            tempOdds = {}
            for cost, odd in oddsByCost.items():
                tempOdds[int(cost)] = odd
            self.odds[int(level)] = tempOdds
