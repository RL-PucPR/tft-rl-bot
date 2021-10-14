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

def train_emulator(load=False):
    db = DDragon()
    acquirer = Emulator(db, Controller(db))
    env = GameStateEnv(acquirer, db)
    model = A2C(MultiInputActorCriticPolicy, env, verbose=1)
    if load:
        model.load("data/model")
    n = 10000
    n_log = 100
    model.learn(total_timesteps=n*5, log_interval=int(n/n_log))
    model.save("data/model")
    obs = env.reset()
    i = 0
    prev = 0
    done = False
    while not done:
        try:
            action, _states = model.predict(obs)
            i += 1
        except RuntimeError:
            continue
        obs, rewards, done, info = env.step(action)
        if rewards == -100:
            continue
        print("Iter: ", i-prev)
        prev = i
        env.render()
    print("\nDONE\n-------------------------------------\n")
    env.render()
    print("Iter: ", i)


def test(load=True):
    db = DDragon()
    acquirer = Emulator(db, Controller(db))
    env = GameStateEnv(acquirer, db)
    model = A2C(MultiInputActorCriticPolicy, env, verbose=1)
    if load:
        model.load("data/teste")
    else:
        n = 1000
        n_log = 10
        model.learn(total_timesteps=n*5, log_interval=int(n/n_log))
    env.set_acquirer(ScreenInterpreter(db, max_time=0.5, speed=0.1))
    i = 0
    prev = 0
    done = False
    obs = env.reset()
    while not done:
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        i += 1
        if rewards == -100:
            continue
        print("Iter: ", i - prev)
        prev = i
        env.render()
    print("\n\nEnd")
    env.render()
    print("Iter: ", i)


if __name__ == '__main__':
    # test_reader()
    # train_emulator(True)
    test()
