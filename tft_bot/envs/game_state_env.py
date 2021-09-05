from abc import ABC

import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
from util import get_board_position
from database import DDragon

REJECTED = DDragon.REJECTED


class GameStateEnv(gym.GoalEnv, ABC):
    metadata = {'render.modes': ['human']}

    def __init__(self, acquirer, database):
        super(GameStateEnv, self).__init__()

        self.acquirer = acquirer
        self.action_functions = [
            self.wait,
            self.refresh_store,
            self.buy_exp,
            self.buy_champion,
            self.sell_from_bench,
            self.sell_from_board,
            self.move_in_bench,
            self.move_in_board,
            self.move_from_bench_to_board,
            self.move_from_board_to_bench,
        ]

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
                "start": spaces.Discrete(4 * 7),
                "end": spaces.Discrete(4 * 7)
            })
        })

        n_champions = len(database.champions)
        # Empty space will be defined as
        # {
        #   "champion": n_champions,
        #   "star": 0
        # }
        champion_space = spaces.Dict({
            "champion": spaces.Discrete(n_champions + 1),
            "star": spaces.Discrete(4)
        })
        self.observation_space = spaces.Dict({
            "board": spaces.Tuple((spaces.Tuple((champion_space,) * 7),) * 4),
            "bench": spaces.Tuple((champion_space,) * 9),
            "store": spaces.Tuple((spaces.Discrete(n_champions + 1),) * 5),
            "gold": spaces.Discrete(128),
            "level": spaces.Discrete(10),
            "xp": spaces.Discrete(80),
            "hp": spaces.Discrete(100 + 1),
            "position": spaces.Discrete(8),
            "timer": spaces.Discrete(30),
            "stage": spaces.Tuple((spaces.Discrete(10), spaces.Discrete(7)))
        })

        self.champion_index = {}
        for i in range(n_champions):
            self.champion_index[database.champions[i]["name"]] = i

    def wait(self, params):
        if params["start"] > 0 or params["end"] > 0:
            return REJECTED
        self.acquirer.wait()
        return 0

    def refresh_store(self, params):
        if params["start"] > 0 or params["end"] > 0:
            return REJECTED
        self.acquirer.refresh_store()
        return 0

    def buy_exp(self, params):
        if params["start"] > 0 or params["end"] > 0:
            return REJECTED
        self.acquirer.buy_exp()
        return 0

    def buy_champion(self, params):
        if params["start"] > 4 or params["end"] > 0:
            return REJECTED
        self.acquirer.buy_champion(params["start"])
        return 0

    def sell_from_bench(self, params):
        if params["start"] > 8 or params["end"] > 0:
            return REJECTED
        self.acquirer.sell_from_bench(params["start"])
        return 0

    def sell_from_board(self, params):
        if params["end"] > 0:
            return REJECTED
        self.acquirer.sell_from_board(get_board_position(params["start"]))
        return 0

    def move_in_bench(self, params):
        if params["start"] > 8 or params["end"] > 8 or params["start"] == params["end"]:
            return REJECTED
        self.acquirer.move_in_bench(params["start"], params["end"])
        return 0

    def move_in_board(self, params):
        if params["start"] == params["end"]:
            return REJECTED
        self.acquirer.move_in_board(get_board_position(params["start"]), get_board_position(params["end"]))
        return 0

    def move_from_bench_to_board(self, params):
        if params["start"] > 8 or params["start"] == params["end"]:
            return REJECTED
        self.acquirer.move_from_bench_to_board(params["start"], get_board_position(params["end"]))
        return 0

    def move_from_board_to_bench(self, params):
        if params["end"] > 8 or params["start"] == params["end"]:
            return REJECTED
        self.acquirer.move_from_board_to_bench(get_board_position(params["start"]), params["end"])
        return 0

    def get_observation(self):
        state = self.acquirer.get_observation()
        n_champions = len(self.champion_index)
        empty_champion = {
            "champion": n_champions,
            "star": 0
        }

        store = ()
        for champion in state["store"]:
            idx = self.champion_index[champion] if champion in self.champion_index else n_champions
            store = store + (idx,)

        bench = ()
        for champion in state['bench']:
            if champion is not None and champion["name"] in self.champion_index:
                aux = {
                    "champion": self.champion_index[champion["name"]],
                    "star": champion["star"]
                }
            else:
                aux = empty_champion
            bench = bench + (aux,)

        board = ()
        for row in state['board']:
            aux_row = ()
            for champion in row:
                if champion is not None and champion["name"] in self.champion_index:
                    aux = {
                        "champion": self.champion_index[champion["name"]],
                        "star": champion["star"]
                    }
                else:
                    aux = empty_champion
                aux_row = aux_row + (aux,)
            board = board + (aux_row,)

        observation = {
            "board": ((empty_champion,) * 7,) * 4,
            "bench": (empty_champion,) * 9,
            "store": store,
            "gold": state["gold"],
            "level": state["level"],
            "xp": state["xp"],
            "hp": state["hp"],
            "position": state["position"],
            "timer": state["timer"],
            "stage": state["stage"],
        }
        return observation, state["done"]

    def step(self, action):
        print(action)
        reward = self.action_functions[action["action"]](action["parameters"])
        observation, done = self.get_observation()
        info = {}
        return observation, reward, done, info

    def reset(self):
        self.acquirer.clear_board()
        self.acquirer.wait()
        return self.get_observation()[0]

    def render(self, mode='human'):
        pass

    # def close(self):
    #     ...
