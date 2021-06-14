import random
import time


class GameState:
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

    def checkBench(self, position):
        return self.data["bench"][position] is not None

    def checkBoard(self, position):
        return self.data["board"][position[0]][position[1]] is not None

    def checkBenchSpace(self):
        for i in range(len(self.data["bench"])):
            if self.data["bench"][i] is None:
                return True
        return False

    def emptyBoardPos(self):
        for i in range(len(self.data["board"])):
            for j in range(len(self.data["board"][i])):
                if self.data["board"][i][j] is not None:
                    return [i, j]

    def countBoard(self):
        count = 0
        for i in range(len(self.data["board"])):
            for j in range(len(self.data["board"][i])):
                if self.data["board"][i][j] is not None:
                    count += 1
        return count

    def randomBenchPosition(self):
        return random.choice(range(len(self.data["bench"])))

    def randomBoardPosition(self):
        xAxis = random.choice(range(len(self.data["board"])))
        yAxis = random.choice(range(len(self.data["board"][xAxis])))
        return xAxis, yAxis

    # Getters
    def getGold(self):
        """
        Returns current gold count (use after update).
        """
        return self.data["gold"]

    def getLevel(self):
        """
        Returns current level (use after update).
        """
        return self.data["level"]

    def getStore(self):
        """
        Returns array containing champions found in store (use after update).
        """
        return self.data["store"]

    def getXpToLevelUp(self):
        """
        Returns the ammount of xp missing for the player to level up (use after update).
        """
        return self.data["xpToLevelUp"]

    def getHp(self):
        """
        Returns current value for the player's hp (use after update).
        """
        return self.data["hp"]

    def update(self):
        self.data["gold"] = self.acquirer.getGold()
        self.data["level"] = self.acquirer.getLevel()
        self.data["store"] = self.acquirer.getStore()
        self.data["xpToLevelUp"] = self.acquirer.getXpToLevelUp()
        self.data["hp"] = self.acquirer.getHp()

    # Setters
    def newChampion(self, champion):
        for i in range(len(self.data["bench"])):
            if self.data["bench"][i] is None:
                self.data["bench"][i] = champion
                if self.countBoard() < self.data["level"]:
                    self.moveFromBenchToBoard(i, self.randomBoardPosition())
                return

    def buyChampion(self, position):
        if not self.checkBenchSpace():
            print("NO SPACE IN BENCH")
            return
        print("BUYING CHAMPION " + str(position))
        self.acquirer.buyChampion(position)
        bought = self.data["store"][position]
        if bought is not None:
            self.data["gold"] = self.acquirer.getGold()
            self.data["store"][position] = None
            self.newChampion(bought)

    def moveFromBenchToBoard(self, start, end):
        if not self.checkBench(start):
            print("EMPTY BENCH SPACE")
            return
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveFromBenchToBoard(start, end)
        aux = self.data["bench"][start]
        self.data["bench"][start] = self.data["board"][end[0]][end[1]]
        self.data["board"][end[0]][end[1]] = aux

    def moveFromBoardToBench(self, start, end):
        if not self.checkBoard(start):
            print("EMPTY BOARD SPACE")
            return
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveFromBoardToBench(start, end)
        aux = self.data["board"][start[0]][start[1]]
        self.data["board"][start[0]][start[1]] = self.data["bench"][end]
        self.data["bench"][end] = aux

    def moveInBench(self, start, end):
        if not self.checkBench(start):
            print("EMPTY BENCH SPACE")
            return
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveInBench(start, end)
        aux = self.data["bench"][start]
        self.data["bench"][start] = self.data["bench"][end]
        self.data["bench"][end] = aux

    def moveInBoard(self, start, end):
        if not self.checkBoard(start):
            print("EMPTY BOARD SPACE")
            return
        print("MOVING FROM "+str(start)+" to "+str(end))
        self.acquirer.moveInBoard(start, end)
        aux = self.data["board"][start[0]][start[1]]
        self.data["board"][start[0]][start[1]] = self.data["board"][end[0]][end[1]]
        self.data["board"][end[0]][end[1]] = aux

    def sellFromBench(self, position):
        if not self.checkBench(position):
            print("EMPTY BENCH SPACE")
            return
        print("SELLING "+str(position))
        self.acquirer.sellFromBench(position)
        self.data["gold"] = self.acquirer.getGold()
        self.data["bench"][position] = None

    def sellFromBoard(self, position):
        if not self.checkBoard(position):
            print("EMPTY BOARD SPACE")
            return
        print("SELLING "+str(position))
        self.acquirer.sellFromBoard(position)
        self.data["gold"] = self.acquirer.getGold()
        self.data["board"][position[0]][position[1]] = None

    def buyExp(self):
        if self.data["gold"] < 4:
            print("NOT ENOUGH GOLD")
            return
        print("BUYING EXP")
        self.acquirer.buyExp()
        self.data["gold"] = self.acquirer.getGold()
        self.data["level"] = self.acquirer.getLevel()
        self.data["xpToLevelUp"] = self.acquirer.getXpToLevelUp()

    def refreshStore(self):
        if self.data["gold"] < 2:
            print("NOT ENOUGH GOLD")
            return
        print("REFRESHING STORE")
        self.acquirer.refreshStore()
        self.data["gold"] = self.acquirer.getGold()
        self.data["store"] = self.acquirer.getStore()

    def wait(self):
        print("WAITING")
        time.sleep(1)
        self.update()

    def __init__(self, acquirer):
        self.acquirer = acquirer


