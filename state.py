import random
import time
import gym
import numpy as np
from gym import spaces


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


class GameState(gym.Env, Setters):
    acquirer = None
    # champion format
    # {
    #     "name": "Vayne",
    #     "star": 2,
    #     "quantity": 1,
    # }
    champions = []
    bench = [None] * 9
    board = [[None] * 7] * 3
    store = [None] * 5
    gold = 0
    level = 1
    xpToLevelUp = 0
    hp = 100
    position = 8
    winner = False

    def randomBenchPosition(self):
        return random.choice(range(len(self.bench)))

    def randomBoardPosition(self):
        xAxis = random.choice(range(len(self.board)))
        yAxis = random.choice(range(len(self.board[xAxis])))
        return xAxis, yAxis

    def update(self):
        self.gold = self.acquirer.getGold()
        self.level = self.acquirer.getLevel()
        self.store = self.acquirer.getStore()
        self.xpToLevelUp = self.acquirer.getXpToLevelUp()
        self.hp, self.position = self.acquirer.getHp()

    def __init__(self, acquirer):
        super(GameState, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        # Environment will have 12 different actions
        # Some actions will take two parameters at most
        # Actions that should not receive parameters that are
        # run with parameters different from 0 will receive
        # instant negative reward
        self.action_space = spaces.Dict({
            "action": spaces.Discrete(12),
            "parameters": spaces.Dict({
                "start": spaces.Discrete(4*7),
                "end": spaces.Discrete(4*7)
            })
        })
        # Example for using image as input:
        self.observation_space = spaces.Dict({
            ""
        })
        self.acquirer = acquirer




