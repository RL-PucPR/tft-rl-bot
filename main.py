from controller import Controller
from screen import ScreenInterpreter
from state import GameState
from player import Player
from time import sleep
from database import DDragon
from tft_bot.envs.game_state_env import GameStateEnv
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines import A2C
from stable_baselines.common.env_checker import check_env


def testReader():
    sleep(1)
    gs = GameState(ScreenInterpreter(speed=0.2))
    player = Player(gs)
    while True:
        gs.update()
        print("Gold: ", gs.getGold())
        print("Level: ", gs.getLevel())
        print("Store: ", gs.getStore())
        print("xp: ", gs.getXpToLevelUp())
        print("Hp: ", gs.getHp())
        player.randomAction()
        sleep(0.1)


def testTrainer():
    c = Controller()
    print(c.pool)
    print(c.odds)
    shop = c.refreshShop([None, None, None, None, None], 1)
    for i in range(9):
        print(shop)
        shop = c.refreshShop(shop, i + 1)


def testEnv():
    env = GameStateEnv(ScreenInterpreter(maxTime=0, speed=0.2), DDragon())
    # It will check your custom environment and output additional warnings if needed
    check_env(env)

if __name__ == '__main__':
    # testTrainer()
    # testReader()
    testEnv()
