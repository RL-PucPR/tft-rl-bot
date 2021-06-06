import random
from controller import Controller
from database import DDragon


class Emulator(Controller):
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

    def change_pool_amount(self, shop, func):
        for cost, championsByCost in self.pool.items():
            for i in range(len(championsByCost)):
                self.pool[cost][i]["amount"] = func(championsByCost[i]["amount"],
                                                    shop.count(championsByCost[i]["championInfo"]["name"]))

    def generate_shop(self, level):
        odds_by_cost = self.odds[level]
        choices = []
        for cost in range(1, 6):
            odd = odds_by_cost[cost] / 100
            for champion in self.pool[cost]:
                choices += [champion["championInfo"]["name"]] * int(champion["amount"] * odd)
        shop = []
        for i in range(5):
            if len(choices) > 0:
                shop.append(random.choices(choices)[0])
            else:
                shop.append(None)
        self.change_pool_amount(shop, lambda a, b: a - b)
        return shop

    def refresh_shop(self, old_shop, level):
        self.change_pool_amount(old_shop, lambda a, b: a + b)
        return self.generate_shop(level)

    def __init__(self, load=False):

        database = DDragon()

        if load:
            request()
            database.load()

        pool_size = {}
        for key, value in database.pool.items():
            pool_size[int(key)] = value

        for champion in database.champions:
            if champion["cost"] > 5:
                continue
            if len(champion["traits"]) > 0 and champion["cost"] <= 5:
                self.pool[champion["cost"]].append({
                    "championInfo": champion,
                    "amount": pool_size[champion["cost"]],
                    "maxAmount": pool_size[champion["cost"]],
                })
            else:
                self.pool[champion["cost"]].append({
                    "championInfo": champion,
                    "amount": 0,
                    "maxAmount": 0,
                })

        for level, oddsByCost in database.odds.items():
            temp_odds = {}
            for cost, odd in oddsByCost.items():
                temp_odds[int(cost)] = odd
            self.odds[int(level)] = temp_odds
