import pyautogui
from controller import Controller
from database import DDragon
from screen import ScreenInterpreter
from time import sleep


def testReader():
    si = ScreenInterpreter()
    while True:
        si.retrieveData(pyautogui.screenshot())
        print(si.getStore())
        print(si.getGold())
        sleep(1)


if __name__ == '__main__':
    print(Controller(DDragon()).pool)
    # testReader()
