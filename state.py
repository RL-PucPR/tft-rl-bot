import random
import time


class Getters:
    acquirer = None
    data = {
        "champions": [],
        "bench": [None] * 9,
        "board": [[None] * 7] * 3,
        "store": [None] * 5,
        "gold": 0,
        "level": 1,
        "xpToLevelUp": 0,
        "hp": 0,
    }

    def getGold(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["gold"]

    def getLevel(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["level"]

    def getStore(self):
        """
        Returns array containing champions found in store (use after retrieval).
        """
        return self.data["store"]

    def getXpToLevelUp(self):
        """
        Returns the ammount of xp missing for the player to level up (use after retrieval).
        """
        return self.data["xpToLevelUp"]

    def getHp(self):
        """
        Returns current value for the player's hp (use after retrieval).
        """
        return self.data["hp"]

    def randomBenchPosition(self):
        return random.choice(range(len(self.data["bench"])))

    def randomBoardPosition(self):
        xAxis = random.choice(range(len(self.data["board"])))
        yAxis = random.choice(range(len(self.data["board"][xAxis])))
        return xAxis, yAxis

    def update(self):
        self.data["gold"] = self.acquirer.getGold()
        self.data["level"] = self.acquirer.getLevel()
        self.data["store"] = self.acquirer.getStore()
        self.data["xpToLevelUp"] = self.acquirer.getXpToLevelUp()
        self.data["hp"] = self.acquirer.getHp()


class Setters:
    acquirer = None

    def buyChampion(self, position=None):
        print("BUYING CHAMPION " + str(position))
        self.acquirer.buyChampion(position)

    def moveFromBenchToBoard(self, start, end):
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveFromBenchToBoard(start, end)

    def moveFromBoardToBench(self, start, end):
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveFromBoardToBench(start, end)

    def moveInBench(self, start, end):
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveInBench(start, end)

    def moveInBoard(self, start, end):
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveInBoard(start, end)

    def sellFromBench(self, position):
        print("SELLING "+str(position))
        self.acquirer.sellFromBench(position)

    def sellFromBoard(self, position):
        print("SELLING "+str(position))
        self.acquirer.sellFromBoard(position)

    def buyExp(self):
        print("BUYING EXP")
        self.acquirer.buyExp()

    def refreshStore(self):
        print("REFRESHING STORE")
        self.acquirer.refreshStore()

    def wait(self):
        print("WAITING")
        time.sleep(1)


class GameState(Getters, Setters):
    # champion format
    # {
    #     "name": "Vayne",
    #     "star": 2,
    #     "quantity": 1,
    # }
    data = {
        "champions": [],
        "bench": [None] * 9,
        "board": [[None] * 7] * 3,
        "store": [None] * 5,
        "gold": 0,
        "level": 1,
        "xpToLevelUp": 0,
        "hp": 0,
    }

    def apply(self, func, *args, **kwargs):
        # TODO - I want to do some actions in gamestate (like buying from the store)
        self.acquirer.func(args, kwargs)
        self.update()

    def __init__(self, acquirer):
        self.acquirer = acquirer


