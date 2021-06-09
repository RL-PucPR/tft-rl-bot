from state import GameState
import random


class Player:
    state = None

    def buyChampion(self, position=None):
        # If no position was given, choose a random number between 1 and 5
        if position is None:
            position = random.choice(range(5)) + 1
        self.state.buyChampion(position)

    def moveFromBenchToBoard(self, start=None, end=None):
        if start is None:
            start = self.state.randomBenchPosition()
        if end is None:
            end = self.state.randomBoardPosition()
        self.state.moveFromBenchToBoard(start, end)

    def moveFromBoardToBench(self, start=None, end=None):
        if start is None:
            start = self.state.randomBoardPosition()
        if end is None:
            end = self.state.randomBenchPosition()
        self.state.moveFromBoardToBench(start, end)

    def moveInBench(self, start=None, end=None):
        if start is None:
            start = self.state.randomBenchPosition()
        if end is None:
            end = self.state.randomBenchPosition()
        self.state.moveInBench(start, end)

    def moveInBoard(self, start=None, end=None):
        if start is None:
            start = self.state.randomBoardPosition()
        if end is None:
            end = self.state.randomBoardPosition()
        self.state.moveInBoard(start, end)

    def randomMove(self):
        random.choice(self.moveFunctions)()

    def sellFromBench(self, position=None):
        if position is None:
            position = self.state.randomBenchPosition()
        self.state.sellFromBench(position)

    def sellFromBoard(self, position=None):
        if position is None:
            position = self.state.randomBoardPosition()
        self.state.sellFromBoard(position)

    def randomSell(self):
        random.choice(self.sellFunctions)()

    def levelUp(self):
        print("LEVEL UP")
        for i in range(self.state.getXpToLevelUp()//4):
            self.state.buyExp()

    def wait(self):
        self.state.wait()

    def randomAction(self):
        random.choice(self.actions)()

    def __init__(self, state):
        self.state = state
        self.sellFunctions = [
            self.sellFromBench,
            self.sellFromBoard,
        ]
        self.moveFunctions = [
            self.moveFromBenchToBoard,
            self.moveFromBoardToBench,
            self.moveInBench,
            self.moveInBoard,
        ]
        self.actions = [
            self.buyChampion,
            self.randomMove,
            self.randomSell,
            self.levelUp,
            self.wait,
        ]

