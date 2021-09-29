import random
from acquirer import Player


class DummyPlayer(Player):

    def __champ_bought(self, champion_name):
        pos = self.__next_available()
        champion = {
            "name": champion_name,
            "star": 1
        }
        if len(pos) > 1:
            self.board[pos[0]][pos[1]] = champion
        else:
            self.bench[pos[0]] = champion
        pos_list = self.__can_merge(pos)
        if pos_list:
            pos = self.__merge(pos_list)
            pos_list = self.__can_merge(pos)
            if pos_list:
                self.__merge(pos_list)

    def buy_champs(self, shop, n):
        for _ in range(n):
            self.__champ_bought(shop.pop(random.randint(0, len(shop)-1)))
        return shop


class Controller:
    # Format:
    # pool = {
    #     cost: [{
    #         championName,
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

    championInfo = {}
    dummy = None

    def __get_champion_id(self, name):
        cost = self.championInfo[name]["cost"]
        for idx in range(len(self.pool[cost])):
            if self.pool[cost][idx]["championName"] == name:
                return idx

    def __change_pool_amount(self, shop, func):
        for champion in list(filter(lambda x: x is not None, shop)):
            cost = self.championInfo[champion]["cost"]
            for idx in range(len(self.pool[cost])):
                if self.pool[cost][idx]["championName"] == champion:
                    self.pool[cost][idx]["amount"] = func(self.pool[cost][idx]["amount"])
                    break

    def __generate_shop(self, level):
        oddsByCost = self.odds[level]
        choices = []
        for cost in range(1, 6):
            odd = oddsByCost[cost] / 100
            for champion in self.pool[cost]:
                choices += [champion["championName"]] * int(champion["amount"] * odd)
        shop = []
        for _ in range(5):
            if len(choices) > 0:
                shop.append(random.choices(choices)[0])
            else:
                shop.append(None)
        self.__change_pool_amount(shop, lambda a: a - 1)
        return shop

    def refresh_shop(self, old_shop, level):
        self.__change_pool_amount(old_shop, lambda a: a + 1)
        if self.dummy is not None and old_shop.count(None) > 0:
            shop = self.__generate_shop(level)
            shop = self.dummy.buy_champs(shop, old_shop.count(None))
            self.__change_pool_amount(shop, lambda a: a + 1)
        return self.__generate_shop(level)

    def battle(self, board):
        if self.battler is None:
            return 1
        return self.battler.battle(board, self.dummy)

    def __init__(self, database, battler=None, multi=False):
        if multi:
            raise NotImplementedError
        else:
            self.dummy = DummyPlayer()

        pool_size = {}
        for key, value in database.pool.items():
            pool_size[int(key)] = value

        for champion in database.champions:
            cost = champion["cost"]
            if cost > 5:
                continue

            self.championInfo[champion["name"]] = champion
            if len(champion["traits"]) > 0 and 0 < cost <= 5:
                self.pool[cost].append({
                    "championName": champion["name"],
                    "amount": pool_size[cost],
                    "maxAmount": pool_size[cost],
                })
            else:
                self.pool[cost].append({
                    "championName": champion["name"],
                    "amount": 0,
                    "maxAmount": 0,
                })

        for level, oddsByCost in database.odds.items():
            tempOdds = {}
            for cost, odd in oddsByCost.items():
                tempOdds[int(cost)] = odd
            self.odds[int(level)] = tempOdds

        self.battler = battler
