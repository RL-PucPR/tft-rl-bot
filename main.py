# from time import sleep

from stable_baselines3 import A2C
from stable_baselines3.common.policies import MultiInputActorCriticPolicy

# from controller import Controller
from database import DDragon
# from player import Player
from screen import ScreenInterpreter
from tft_bot.envs.game_state_env import GameStateEnv


# def test_reader():
#     sleep(1)
#     si = ScreenInterpreter(database=DDragon().load(), max_time=2, speed=0.2)
#     player = Player(si)
#     while True:
#         si.refresh()
#         print(si.get_observation())
#         player.randomAction()
#         si.fill_board()
#         sleep(0.5)
#
#
# def test_trainer():
#     c = Controller()
#     print(c.pool)
#     print(c.odds)
#     shop = c.refreshShop([None, None, None, None, None], 1)
#     for i in range(9):
#         print(shop)
#         shop = c.refreshShop(shop, i + 1)


def test_env():
    db = DDragon()
    env = GameStateEnv(ScreenInterpreter(db, max_time=1, speed=0.2), db)
    # It will check your custom environment and output additional warnings if needed
    # check_env(env)
    model = A2C(MultiInputActorCriticPolicy, env, verbose=1)
    model.learn(total_timesteps=20000)
    obs = env.reset()
    for i in range(2000):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        env.render()


if __name__ == '__main__':
    # test_trainer()
    # test_reader()
    test_env()
