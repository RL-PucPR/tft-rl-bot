import random


class FakePlayer:
    plays = []

    def randomBenchPosition(self):
        return random.choice(range(9))

    def randomBoardPosition(self):
        return [random.choice(range(4)), random.choice(range(7))]

    def buyChampion(self, position=None):
        # If no position was given, choose a random number between 1 and 5
        if position is None:
            position = random.choice(range(5))
        print("BUYING", position)
        self.acquirer.buy_champion(position)

    def moveFromBenchToBoard(self, start=None, end=None):
        if start is None:
            start = self.randomBenchPosition()
        if end is None:
            end = self.randomBoardPosition()
        print("MOVING", start, end)
        self.acquirer.move_from_bench_to_board(start, end)

    def moveFromBoardToBench(self, start=None, end=None):
        if start is None:
            start = self.randomBoardPosition()
        if end is None:
            end = self.randomBenchPosition()
        print("MOVING", start, end)
        self.acquirer.move_from_board_to_bench(start, end)

    def moveInBench(self, start=None, end=None):
        if start is None:
            start = self.randomBenchPosition()
        if end is None:
            end = self.randomBenchPosition()
        print("MOVING", start, end)
        self.acquirer.move_in_bench(start, end)

    def moveInBoard(self, start=None, end=None):
        if start is None:
            start = self.randomBoardPosition()
        if end is None:
            end = self.randomBoardPosition()
        print("MOVING", start, end)
        self.acquirer.move_in_board(start, end)

    def move(self, index=None):
        if index is None:
            random.choice(self.moveFunctions)()
        else:
            self.moveFunctions[index]()

    def sellFromBench(self, position=None):
        if position is None:
            position = self.randomBenchPosition()
        print("SELLING", position)
        self.acquirer.sell_from_bench(position)

    def sellFromBoard(self, position=None):
        if position is None:
            position = self.randomBoardPosition()
        print("SELLING", position)
        self.acquirer.sell_from_board(position)

    def sell(self, index=None):
        if index is None:
            random.choice(self.sellFunctions)()
        else:
            self.moveFunctions[index]()

    def levelUp(self):
        print("BUYING XP")
        self.acquirer.buy_exp()

    def refreshStore(self):
        print("REFRESHING")
        self.acquirer.refresh_store()

    def wait(self):
        print("WAIT")
        self.acquirer.wait()

    def randomAction(self):
        return random.choice(self.actions)()

    def __init__(self, acquirer):
        self.acquirer = acquirer
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
            self.move,
            self.sell,
            # self.levelUp,
            # self.refreshStore,
            # self.wait,
        ]
