import random
from acquirer import Player


class DummyPlayer(Player):
    champsOnBoard = 0
    hp = 100

    def __champ_bought(self, champion_name):
        pos = self.next_available()
        champion = {
            "name": champion_name,
            "star": 1
        }
        if len(pos) > 1:
            self.board[pos[0]][pos[1]] = champion
            self.champsOnBoard += 1
        else:
            self.bench[pos[0]] = champion
        pos_list = self.can_merge(pos)
        if pos_list:
            pos = self.merge(pos_list)
            pos_list = self.can_merge(pos)
            if pos_list:
                self.merge(pos_list)

    def buy_champs(self, shop, n):
        for _ in range(n):
            self.__champ_bought(shop.pop(random.randint(0, len(shop)-1))["name"])
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

    def __change_pool_amount(self, champion, func):
        if "star" in champion:
            star = champion["star"]
        else:
            star = 1
        cost = self.championInfo[champion["name"]]["cost"]
        for idx in range(len(self.pool[cost])):
            if self.pool[cost][idx]["championName"] == champion["name"]:
                for _ in range(star):
                    self.pool[cost][idx]["amount"] = func(self.pool[cost][idx]["amount"])
                return

    def __change_pool_amount_shop(self, shop, func):
        for champion in list(filter(lambda x: x is not None, shop)):
            self.__change_pool_amount(champion, func)

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
                champion = random.choices(choices)[0]
                shop.append({"name": champion, "price": self.championInfo[champion]["cost"]})
            else:
                shop.append(None)
        self.__change_pool_amount_shop(shop, lambda a: a - 1)
        return shop

    def sell_champ(self, champion):
        star = champion["star"]
        cost = self.championInfo[champion["name"]]["cost"]
        self.__change_pool_amount(champion, lambda a: a + 1)
        if star == 1:
            return cost
        value = 3 ** (star - 1)
        if cost == 1:
            return value
        return cost * value - 1

    def buy_exp(self, level, xp):
        lvl = level
        newXp = xp["actual"] + 4
        required = xp["required"]
        if xp["required"] < newXp:
            lvl += 1
            newXp = newXp % xp["required"]
            required = self.requiredExp[lvl]
        return lvl, {"actual": newXp, "required": required}

    def refresh_shop(self, old_shop, level):
        self.__change_pool_amount_shop(old_shop, lambda a: a + 1)
        if self.dummy is not None and old_shop.count(None) > 0 and self.dummy.champsOnBoard < level:
            shop = self.__generate_shop(level)
            shop = self.dummy.buy_champs(shop, old_shop.count(None))
            self.__change_pool_amount_shop(shop, lambda a: a + 1)
        return self.__generate_shop(level)

    def __battle(self, board):
        # If self.dummy is not None, use it as opposing board
        # If self.dummy is None, await for another battle call and use both as opponents
        if self.dummy is None:
            raise NotImplementedError
        else:
            opp_board = self.dummy.board
        # If result == 0 -> Draw
        # If result > 0 -> Win
        # If result < 0 -> Loss
        result = 0
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] is not None:
                    result += board[i][j]["star"]
                if opp_board[i][j] is not None:
                    result -= opp_board[i][j]["star"]
        return result

    def wait(self, emulator):
        result = self.__battle(emulator.board)
        if result > 0:
            emulator.gold += 1
            if self.dummy.hp < (2 + result):
                emulator.position = 0
                emulator.done = True
                return
            self.dummy.hp -= (2 + result)
        elif result < 0:
            if emulator.hpList[emulator.position] < (2 + result):
                emulator.hpList[emulator.position] = 0
                emulator.position = 1
                emulator.done = True
                return
            emulator.hpList[emulator.position] -= (2 + result)
        else:
            if self.dummy.hp < 2:
                emulator.position = 0
                emulator.done = True
                return
            self.dummy.hp -= 2
            if emulator.hpList[emulator.position] < 2:
                emulator.hpList[emulator.position] = 0
                emulator.position = 2
                emulator.done = True
                return
            emulator.hpList[emulator.position] -= 2

        if emulator.hpList[emulator.position] < self.dummy.hp:
            emulator.hpList[1] = emulator.hpList[emulator.position]
            emulator.position = 1
            emulator.hpList[0] = self.dummy.hp
        else:
            emulator.hpList[0] = emulator.hpList[emulator.position]
            emulator.position = 0
            emulator.hpList[1] = self.dummy.hp

        emulator.gold += 5

        lvl = emulator.level
        if lvl < 9:
            newXp = emulator.xp["actual"] + 2
            required = emulator.xp["required"]
            if emulator.xp["required"] < newXp:
                lvl += 1
                newXp = newXp % emulator.xp["required"]
                required = self.requiredExp[lvl]
            emulator.level = lvl
            emulator.xp = {"actual": newXp, "required": required}

        emulator.stage[1] += 1
        if emulator.stage[1] > 7:
            emulator.stage[0] += 1
            emulator.stage[1] = 1

        emulator.store = self.refresh_shop(emulator.store, emulator.level)

        emulator.timer = 30

    def __init__(self, database, multiprocessing=False):
        if multiprocessing:
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

        self.requiredExp = database.requiredExp
