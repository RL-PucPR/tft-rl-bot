from abc import ABC

import gym
from gym import spaces

from util import get_board_position


class GameStateEnv(gym.GoalEnv, ABC):
    metadata = {'render.modes': ['human']}

    def __init__(self, acquirer, database):
        super(GameStateEnv, self).__init__()

        self.rejectedReward = database.rewardValues["rejected"]
        self.minReward = min(database.rewardValues.values())
        self.maxReward = max(database.rewardValues.values())
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
        self.action_space = spaces.MultiDiscrete([
            len(self.action_functions),  # Action
            4 * 7,  # Start
            4 * 7  # End
        ])

        n_champions = len(database.champions)
        # Empty space will be defined as
        # {
        #   "champion": n_champions,
        #   "star": 0
        # }
        champion_space = (n_champions + 1) * 4  # Champion: n // 4 | Star: n % 4
        self.observation_space = spaces.Dict({
            'observation': spaces.MultiDiscrete([
                champion_space,  # Board00
                champion_space,  # Board01
                champion_space,  # Board02
                champion_space,  # Board03
                champion_space,  # Board04
                champion_space,  # Board05
                champion_space,  # Board06
                champion_space,  # Board10
                champion_space,  # Board11
                champion_space,  # Board12
                champion_space,  # Board13
                champion_space,  # Board14
                champion_space,  # Board15
                champion_space,  # Board16
                champion_space,  # Board20
                champion_space,  # Board21
                champion_space,  # Board22
                champion_space,  # Board23
                champion_space,  # Board24
                champion_space,  # Board25
                champion_space,  # Board26
                champion_space,  # Board30
                champion_space,  # Board31
                champion_space,  # Board32
                champion_space,  # Board33
                champion_space,  # Board34
                champion_space,  # Board35
                champion_space,  # Board36
                champion_space,  # Bench0
                champion_space,  # Bench1
                champion_space,  # Bench2
                champion_space,  # Bench3
                champion_space,  # Bench4
                champion_space,  # Bench5
                champion_space,  # Bench6
                champion_space,  # Bench7
                champion_space,  # Bench8
                n_champions + 1,  # Store0
                n_champions + 1,  # Store1
                n_champions + 1,  # Store2
                n_champions + 1,  # Store3
                n_champions + 1,  # Store4
                128,  # Gold
                10,  # Level
                80,  # XP
                100 + 1,  # HP
                8,  # Position
                30,  # Timer
                108  # Stage (n // 10 - n % 10)
            ]),
            'achieved_goal': spaces.MultiDiscrete([
                100 + 1,  # HP
                8,  # Position
                self.maxReward - self.minReward + 1,  # Reward
            ]),
            'desired_goal': spaces.MultiDiscrete([
                100 + 1,  # HP
                8,  # Position
                self.maxReward - self.minReward + 1,  # Reward
            ]),
        })

        self.champion_index = {}
        for i in range(n_champions):
            self.champion_index[database.champions[i]["name"]] = i

    def wait(self, params):
        # if params["start"] > 0 or params["end"] > 0:
        #     return self.rejectedReward
        return self.acquirer.wait()

    def refresh_store(self, params):
        # if params["start"] > 0 or params["end"] > 0:
        #     return self.rejectedReward
        return self.acquirer.refresh_store()

    def buy_exp(self, params):
        # if params["start"] > 0 or params["end"] > 0:
        #     return self.rejectedReward
        return self.acquirer.buy_exp()

    def buy_champion(self, params):
        # if params["start"] > 4 or params["end"] > 0:
        #     return self.rejectedReward
        return self.acquirer.buy_champion(params["start"] % 5)

    def sell_from_bench(self, params):
        # if params["start"] > 8 or params["end"] > 0:
        #     return self.rejectedReward
        return self.acquirer.sell_from_bench(params["start"] % 9)

    def sell_from_board(self, params):
        # if params["end"] > 0:
        #     return self.rejectedReward
        return self.acquirer.sell_from_board(get_board_position(params["start"]))

    def move_in_bench(self, params):
        # if params["start"] > 8 or params["end"] > 8:
        #     return self.rejectedReward
        if params["start"] == params["end"]:
            return self.rejectedReward
        return self.acquirer.move_in_bench(params["start"] % 9, params["end"] % 9)

    def move_in_board(self, params):
        if params["start"] == params["end"]:
            return self.rejectedReward
        return self.acquirer.move_in_board(get_board_position(params["start"]), get_board_position(params["end"]))

    def move_from_bench_to_board(self, params):
        # if params["start"] > 8:
        #     return self.rejectedReward
        return self.acquirer.move_from_bench_to_board(params["start"] % 9, get_board_position(params["end"]))

    def move_from_board_to_bench(self, params):
        # if params["end"] > 8:
        #     return self.rejectedReward
        return self.acquirer.move_from_board_to_bench(get_board_position(params["start"]), params["end"] % 9)

    def get_observation(self):
        desired_goal = (
            self.acquirer.hpList[self.acquirer.position],
            0,
        )
        state = self.acquirer.get_observation()
        n_champions = len(self.champion_index)
        empty_champion = {
            "champion": n_champions,
            "star": 0
        }

        store = ()
        for champion in state["store"]:
            if champion is not None and champion["name"] in self.champion_index:
                idx = self.champion_index[champion["name"]]
            else:
                idx = n_champions
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
            bench = bench + (aux["champion"] * 4 + aux["star"],)

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
                aux_row = aux_row + (aux["champion"] * 4 + aux["star"],)
            board = board + (aux_row,)

        observation = (
            board[0][0],
            board[0][1],
            board[0][2],
            board[0][3],
            board[0][4],
            board[0][5],
            board[0][6],
            board[1][0],
            board[1][1],
            board[1][2],
            board[1][3],
            board[1][4],
            board[1][5],
            board[1][6],
            board[2][0],
            board[2][1],
            board[2][2],
            board[2][3],
            board[2][4],
            board[2][5],
            board[2][6],
            board[3][0],
            board[3][1],
            board[3][2],
            board[3][3],
            board[3][4],
            board[3][5],
            board[3][6],
            bench[0],
            bench[1],
            bench[2],
            bench[3],
            bench[4],
            bench[5],
            bench[6],
            bench[7],
            bench[8],
            store[0],
            store[1],
            store[2],
            store[3],
            store[4],
            state["gold"],
            state["level"],
            state["xp"],
            state["hp"],
            state["position"],
            state["timer"],
            state["stage"][0] * 10 + state["stage"][1],
        )

        achieved_goal = (
            state["hp"],
            state["position"]
        )

        goal_observation = {
            "observation": observation,
            "achieved_goal": achieved_goal,
            "desired_goal": desired_goal,
        }

        return goal_observation, state["done"]

    def step(self, action):
        reward = self.action_functions[action[0]]({"start": action[1], "end": action[2]})
        print(action, reward)
        observation, done = self.get_observation()
        observation["achieved_goal"] += (reward - self.minReward,)
        observation["desired_goal"] += (self.maxReward - self.minReward,)
        info = {}
        return observation, reward, done, info

    def reset(self):
        super().reset()
        self.acquirer.clear_board()
        self.acquirer.wait()
        observation = self.get_observation()[0]
        observation["achieved_goal"] += (0 - self.minReward,)
        observation["desired_goal"] += (0 - self.minReward,)
        return observation

    def compute_reward(self, achieved_goal, desired_goal, info):
        return achieved_goal[2] + self.minReward

    def render(self, mode='human'):
        print(self.get_observation()[0])

    # def close(self):
    #     ...
