from time import sleep

from stable_baselines3 import A2C
from stable_baselines3.common.policies import MultiInputActorCriticPolicy

from controller import Controller
from database import DDragon
from fakeplayer import FakePlayer
from emulator import Emulator
from screen import ScreenInterpreter
from tft_bot.envs.game_state_env import GameStateEnv


# def test_reader():
#     sleep(1)
#     si = ScreenInterpreter(database=DDragon().load(), max_time=2, speed=0.2)
#     player = FakePlayer(si)
#     while True:
#         si.refresh()
#         print(si.get_observation())
#         player.randomAction()
#         si.fill_board()
#         sleep(0.5)

def test():
    db = DDragon()
    acquirer = Emulator(db, Controller(db))
    env = GameStateEnv(acquirer, db)
    # It will check your custom environment and output additional warnings if needed
    # check_env(env)
    model = A2C(MultiInputActorCriticPolicy, env, verbose=1)
    model.learn(total_timesteps=200000)
    env = GameStateEnv(ScreenInterpreter(db, max_time=1, speed=0.2), db)
    for _ in range(10):
        i = 0
        done = False
        obs = env.reset()
        while not done:
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action)
            i += 1
            # if action[0] == 0:
            #     print("Iteração: "+str(i))
            #     print(">>")
            #     env.render()
        print("\n\nEnd")
        env.render()


def test_emulator(load=False):
    db = DDragon()
    acquirer = Emulator(db, Controller(db))
    env = GameStateEnv(acquirer, db)
    # It will check your custom environment and output additional warnings if needed
    # check_env(env))
    model = A2C(MultiInputActorCriticPolicy, env, verbose=1)
    n = 10000
    n_log = 10
    if load:
        model.load("data/teste")
    else:
        model.learn(total_timesteps=n*5, log_interval=int(n/n_log))
        model.save("data/teste")
    obs = env.reset()
    # for i in range(20000):
    done = False
    while not done:
        try:
            action, _states = model.predict(obs)
        except RuntimeError:
            continue
        obs, rewards, done, info = env.step(action)
        # if i % 100 > 0 and rewards == -100:
        if rewards == -100:
            continue
        if action[0] == 8:
            print("\nAction: ", action)
            print("Reward: ", rewards)
            env.render()
        if done:
            print("\nDONE\n-------------------------------------\n")
            env.render()
            obs = env.reset()


if __name__ == '__main__':
    # test_reader()
    # test()
    test_emulator(True)
