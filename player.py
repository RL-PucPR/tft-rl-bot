from state import GameState
import random


class Player:
    plays = []

    def buyChampion(self, position=None):
        # If no position was given, choose a random number between 1 and 5
        if position is None:
            position = random.choice(range(5))
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

    def move(self, index=None):
        if index is None:
            random.choice(self.moveFunctions)()
        else:
            self.moveFunctions[index]()

    def sellFromBench(self, position=None):
        if position is None:
            position = self.state.randomBenchPosition()
        self.state.sellFromBench(position)

    def sellFromBoard(self, position=None):
        if position is None:
            position = self.state.randomBoardPosition()
        self.state.sellFromBoard(position)

    def sell(self, index=None):
        if index is None:
            random.choice(self.sellFunctions)()
        else:
            self.moveFunctions[index]()

    def levelUp(self):
        print("LEVEL UP")
        for i in range(self.state.XpToLevelUp//4):
            self.state.buyExp()

    def refreshStore(self):
        self.state.refreshStore()

    def wait(self):
        self.state.wait()

    def randomAction(self):
        return random.choice(self.actions)

    def getBestAction(self):
        # TODO - Search for similar situation from this state and choose the best action
        return None

    def recordGame(self, position):
        # Is the position in which the player finished the game
        # The lower the position, the better
        pass

    def play(self):
        while self.state.hp > 0 and not self.state.winner:
            action = self.getBestAction()
            if action is None:
                action = self.randomAction()
            action()
        self.recordGame(self.state.position)

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
            self.move,
            self.sell,
            self.levelUp,
            self.refreshStore,
            self.wait,
        ]

    def action(self, param):
        store_size = 5
        bench_size = 9
        board_height = 4
        board_width = 7
        board_size = (board_height*board_width)

        index = 0
        if param == index:
            self.wait()
            return
        index += 1
        if param == index:
            self.refreshStore()
            return
        index += 1
        if param == index:
            self.levelUp()
            return
        index += 1
        if param < index+store_size:
            self.buyChampion(param-index)
            return
        index += store_size
        if param < index+bench_size:
            self.sellFromBench(param-index)
            return
        index += bench_size
        if param < index+board_size:
            position = param - index
            self.sellFromBoard((int(position / board_width), position % board_width))
            return
        index += board_size
        if param < index+bench_size*bench_size:
            position = param - index
            self.moveInBench(int(position / bench_size), position % bench_size)
            return
        index += bench_size*bench_size
        if param < index+bench_size*board_size:
            position = param - index
        #     destination = position - bench_size
        #     self.moveFromBenchToBoard(position % bench_size, (int(destination / board_width), destination % board_width))
        #     return
        # index += bench_size*board_size
        # if param < index+bench_size*bench_size:
        #     position = param - index
        #     destination = position - bench_size
        #     self.moveFromBenchToBoard(position % bench_size, (int(destination / board_width), destination % board_width))
        #     return
        #
        # 1+1+1+5+9+4*7+(9+4*7)*(9+4*7-1)
        # # Since the functions have different types of parameters, it will all be reduced to integers
        # 0 self.wait,
        # 1 self.refreshStore,
        # 2 self.levelUp,
        # 3~7 self.buyChampion, [0-4]             # Param: integer for store position
        # 8~16 self.sell, [0-8]                    # Param: integer for bench position
        # 17~23 self.sell, [0][0-6]               # Param: tuple of size 2 for board position
        # 24~30 self.sell, [1][0-6]               # Param: tuple of size 2 for board position
        # 31~37 self.sell, [2][0-6]               # Param: tuple of size 2 for board position
        # 38~44 self.sell, [3][0-6]               # Param: tuple of size 2 for board position
        # 45~53 self.move, [0] [0-8]              # Param1: integer for bench position - Param2: integer for bench destination
        # 45~53 self.move, [1-8] [0-8]              # Param1: integer for bench position - Param2: integer for bench destination
        # self.move, [0-8] [0-3][0-6]         # Param1: integer for bench position - Param2: tuple of size 2 for board destination
        # self.move, [0-3][0-6] [0-8]         # Param1: tuple of size 2 for board position - Param2: integer for bench destination
        # self.move, [0-3][0-6] [0-3][0-6]    # Param1: tuple of size 2 for board position - Param2: tuple of size 2 for board destination
        #
        # self.shape = (len(self.actions), max(len(self.sellFunctions), len(self.moveFunctions)), )
        #
