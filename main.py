from controller import Controller
from screen import ScreenInterpreter
from state import GameState
from player import Player
from time import sleep


def testReader():
    gs = GameState(ScreenInterpreter())
    player = Player(gs)
    while True:
        gs.update()
        print(gs.getGold())
        print(gs.getLevel())
        print(gs.getStore())
        print(gs.getXpToLevelUp())
        print(gs.getHp())
        player.randomAction()
        sleep(1)


def testTrainer():
    c = Controller()
    print(c.pool)
    print(c.odds)
    shop = c.refreshShop([None, None, None, None, None], 1)
    for i in range(9):
        print(shop)
        shop = c.refreshShop(shop, i + 1)


if __name__ == '__main__':
    # testTrainer()
    testReader()
    # testPlayer()
