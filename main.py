from controller import Controller
from screen import ScreenInterpreter
from time import sleep


def testReader():
    si = ScreenInterpreter()
    while True:
        print(si.getStore())
        print(si.getGold())
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
