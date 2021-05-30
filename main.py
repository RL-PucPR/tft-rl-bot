from emulator import Emulator
from screen import ScreenInterpreter
from time import sleep


def test_reader():
    si = ScreenInterpreter()
    while True:
        print(si.get_store())
        print(si.get_gold())
        sleep(1)


def test_trainer():
    c = Emulator()
    print(c.pool)
    print(c.odds)
    shop = c.refresh_shop([None, None, None, None, None], 1)
    for i in range(9):
        print(shop)
        shop = c.refresh_shop(shop, i + 1)


if __name__ == '__main__':
    # test_trainer()
    test_reader()
