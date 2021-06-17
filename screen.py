# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
import PIL.ImageOps
import pytesseract      # Image interpreter
import pyautogui        # Screen manipulation
import time
from acquirer import Acquirer
from database import requiredExp


def read(img, blacklist=".,", whitelist=None):
    """
    Performs the tesseract operation on a cropped image after inversion and desaturation.
    """
    if whitelist:
        return pytesseract.image_to_string(
            img, config="-c tessedit_char_whitelist=" + whitelist
        )
    else:
        return pytesseract.image_to_string(
            img, config="-c tessedit_char_blacklist=" + blacklist
        )


def cropAndEdit(img, x1, y1, x2, y2):
    """
    Crops, inverts, and desaturates image.
    """
    img1 = PIL.ImageOps.invert(img.crop((x1, y1, x2, y2)))
    img1 = img1.convert("LA")
    img1.save("tmp/out.png")
    return img1


def leftClick(delay=0.1):
    pyautogui.mouseDown()
    time.sleep(delay)
    pyautogui.mouseUp()


class ScreenInterpreter:
    # ScreenInterpreter will only work with the game running in fullscreen

    # constructor
    def __init__(self, maxTime=2, keyboard=False, speed=0.1):
        super().__init__()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # track relevant data on the frame
        w, h = pyautogui.size()  # Get the size of the primary monitor.
        self.screen = {
            "width": w,
            "height": h,
        }
        self.screenshot = {
            "screenshot": pyautogui.screenshot("tmp/in.png"),
            "timestamp": 0,
        }
        self.maxTime = maxTime
        self.store = [None] * 5
        self.level = 1
        self.gold = 0
        self.xp = {
            "actual": 0,
            "required": 0,
        }
        self.hpList = [100] * 8
        self.position = 7
        self.done = False
        self.requiredExp = requiredExp()
        self.useKeyboard = keyboard
        self.mouseSpeed = speed
        self.fetchFunctions = [
            self.fetchStore,
            self.fetchLevel,
            self.fetchGold,
            self.fetchExp,
            self.fetchHp,
        ]

    # Internal functions - called by refresh
    def fetchStore(self):
        # run tesseract to locate text
        # recognize champs in store
        upperHeightMod = 1041/1080
        lowerHeightMod = 1069/1080
        leftWidthMod = 485/1920
        nameWidthMod = 140/1920
        storeWidthMod = 201/1920
        x = self.screen['width']*leftWidthMod
        for i in range(5):
            name = read(
                cropAndEdit(
                    self.screenshot["screenshot"],
                    x,
                    self.screen['height'] * upperHeightMod,
                    x + self.screen['width'] * nameWidthMod,
                    self.screen['height'] * lowerHeightMod
                )
            ).replace("\x0c", "").replace("\n", "").replace(" ", "")
            self.store[i] = name if name != "" else None
            x += self.screen['width'] * storeWidthMod

    def fetchLevel(self):
        # see  level
        upperHeightMod = 880/1080
        lowerHeightMod = 908/1080
        leftWidthMod = 314/1920
        rightWidthMod = 345/1920
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        ss = (
            cropAndEdit(
                self.screenshot["screenshot"],
                self.screen['width'] * leftWidthMod,
                self.screen['height'] * upperHeightMod,
                self.screen['width'] * rightWidthMod,
                self.screen['height'] * lowerHeightMod
            )
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        strLevel = read(ss, whitelist="0123456789")
        if len(strLevel) < 1:
            strLevel = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            self.level = int(strLevel)
        except:
            pass

    def fetchGold(self):
        # see gold
        upperHeightMod = 881/1080
        lowerHeightMod = 910/1080
        leftWidthMod = 872/1920
        rightWidthMod = 906/1920
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        ss = (
            cropAndEdit(
                self.screenshot["screenshot"],
                self.screen['width'] * leftWidthMod,
                self.screen['height'] * upperHeightMod,
                self.screen['width'] * rightWidthMod,
                self.screen['height'] * lowerHeightMod
            )
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        strGold = read(ss, whitelist="0123456789")
        if len(strGold) < 1:
            strGold = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            self.gold = int(strGold)
        except:
            pass

    def fetchTimer(self):
        # see timer
        upperHeightMod = 10/1080
        lowerHeightMod = 32/1080
        leftWidthMod = 1142/1920
        rightWidthMod = 1172/1920
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        ss = (
            cropAndEdit(
                self.screenshot["screenshot"],
                self.screen['width'] * leftWidthMod,
                self.screen['height'] * upperHeightMod,
                self.screen['width'] * rightWidthMod,
                self.screen['height'] * lowerHeightMod
            )
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        strTimer = read(ss, whitelist="0123456789")
        if len(strTimer) < 1:
            strTimer = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            return int(strTimer)
        except:
            return 0

    def fetchExp(self):
        # run tesseract to locate text
        # recognize champs in store
        upperHeightMod = 882/1080
        lowerHeightMod = 908/1080
        if self.requiredExp[self.level] < 10:
            leftWidthMod = 410/1920
            rightWidthMod = 432/1920
        else:
            leftWidthMod = 405/1920
            rightWidthMod = 425/1920
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        ss = (
            cropAndEdit(
                self.screenshot["screenshot"],
                self.screen['width'] * leftWidthMod,
                self.screen['height'] * upperHeightMod,
                self.screen['width'] * rightWidthMod,
                self.screen['height'] * lowerHeightMod
            )
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        strExp = read(ss, whitelist="0123456789")
        if len(strExp) < 1:
            strExp = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            self.xp["actual"] = int(strExp)
            if self.xp["actual"] >= self.xp["required"]:
                self.xp["actual"] = 0
        except:
            pass

    def fetchHp(self):
        upperHeightMod = 207/1080
        leftWidthMod = 1775/1920
        rightWidthMod = 1827/1920
        oppLeftWidthMod = 1823/1920
        oppRightWidthMod = 1847/1920
        hpHeightMod = 35/1080
        playerHeightMod = 72/1080
        x = self.screen['height'] * upperHeightMod
        thresh = 150
        fn = lambda a: 255 if a > thresh else 0
        for i in range(8):
            # Check for opponent's hp
            ss = (
                cropAndEdit(
                    self.screenshot["screenshot"],
                    self.screen['width'] * oppLeftWidthMod,
                    x,
                    self.screen['width'] * oppRightWidthMod,
                    x + self.screen['height'] * hpHeightMod
                )
                .resize((200, 200), Image.ANTIALIAS)
                .convert("L")
                .point(fn, mode="1")
            )
            strHp = read(ss, whitelist="0123456789")
            if len(strHp) < 1:
                strHp = pytesseract.image_to_string(ss,
                                config="--psm 10 -c tessedit_char_whitelist=0123456789")
            try:
                intHp = int(strHp)
                if intHp <= 100:
                    self.hpList[i] = intHp
                    if intHp == 0 and self.position < i:
                        if self.position == 0 and self.position == i-1:
                            self.done = True
                        return
            except:
                # If no number was found, check for your hp
                ss = (
                    cropAndEdit(
                        self.screenshot["screenshot"],
                        self.screen['width'] * leftWidthMod,
                        x,
                        self.screen['width'] * rightWidthMod,
                        x + self.screen['height'] * hpHeightMod
                    )
                        .resize((200, 200), Image.ANTIALIAS)
                        .convert("L")
                        .point(fn, mode="1")
                )
                strHp = read(ss, whitelist="0123456789")
                if len(strHp) < 1:
                    strHp = pytesseract.image_to_string(ss,
                                                        config="--psm 10 -c tessedit_char_whitelist=0123456789")
                try:
                    intHp = int(strHp)
                    if intHp <= 100:
                        self.hpList[i] = intHp
                        self.position = i
                        if intHp == 0:
                            self.done = True
                            return
                except:
                    pass
            x += self.screen['height'] * playerHeightMod

    # main function: reads data from in-game screenshot
    def refresh(self):
        """
        Refresh screenshot if old enough.
        Defined by self.maxTime.
        """
        now = time.time()
        if now - self.screenshot["timestamp"] > self.maxTime:
            self.screenshot = {
                "screenshot": pyautogui.screenshot("tmp/in.png"),
                "timestamp": now,
            }

    # Functions to be called by GameState
    # Getters
    def getStore(self):
        self.refresh()
        self.fetchStore()
        return self.store

    def getLevel(self):
        self.refresh()
        self.fetchLevel()
        return self.level

    def getGold(self):
        self.refresh()
        self.fetchGold()
        return self.gold

    def getExpToLevelUp(self):
        self.refresh()
        self.fetchExp()
        return self.xp["required"] - self.xp["actual"]

    def getHp(self):
        self.refresh()
        self.fetchHp()
        return self.hp[self.position], self.position

    def get_observation(self):
        self.refresh()
        for fetch in self.fetchFunctions:
            fetch()
        return {
            "store": self.store,
            "gold": self.gold,
            "level": self.level,
            "xp": self.xp["actual"],
            "hp": self.hpList[self.position],
            "position": self.position,
            "done": self.done
        }

    # Setters
    def buy_champion(self, position):
        baseWidth = 575
        height = 995
        modifier = 200
        pyautogui.moveTo(baseWidth+modifier*position, height, duration=self.mouseSpeed)
        leftClick()

    def toBench(self, action, position):
        baseWidth = 425
        height = 777
        modifier = 118
        action(baseWidth+modifier*position, height, duration=self.mouseSpeed)

    def toBoard(self, action, position):
        if position[0] == 0:
            baseWidth = 575
            height = 675
            modifier = 130
        elif position[0] == 1:
            baseWidth = 530
            height = 590
            modifier = 125
        elif position[0] == 2:
            baseWidth = 605
            height = 510
            modifier = 120
        elif position[0] == 3:
            baseWidth = 560
            height = 440
            modifier = 115
        else:
            return

        action(baseWidth+modifier*position[1], height, duration=self.mouseSpeed)

    def move_from_bench_to_board(self, start, end):
        self.toBench(pyautogui.moveTo, start)
        self.toBoard(pyautogui.dragTo, end)

    def move_from_board_to_bench(self, start, end):
        self.toBoard(pyautogui.moveTo, start)
        self.toBench(pyautogui.dragTo, end)

    def move_in_bench(self, start, end):
        self.toBench(pyautogui.moveTo, start)
        self.toBench(pyautogui.dragTo, end)

    def move_in_board(self, start, end):
        self.toBoard(pyautogui.moveTo, start)
        self.toBoard(pyautogui.dragTo, end)

    def sell_from_bench(self, position):
        self.toBench(pyautogui.moveTo, position)
        if self.useKeyboard:
            pyautogui.press("e")
        else:
            pyautogui.dragTo(900, 1000, duration=self.mouseSpeed)

    def sell_from_board(self, position):
        self.toBoard(pyautogui.moveTo, position)
        if self.useKeyboard:
            pyautogui.press("e")
        else:
            pyautogui.dragTo(900, 1000, duration=self.mouseSpeed)

    def buy_exp(self):
        if self.useKeyboard:
            pyautogui.press("f")
        else:
            pyautogui.moveTo(370, 960, duration=self.mouseSpeed)
            leftClick()

    def refresh_store(self):
        if self.useKeyboard:
            pyautogui.press("d")
        else:
            pyautogui.moveTo(360, 1030, duration=self.mouseSpeed)
            leftClick()

    def clear_board(self):
        initial_mouse_speed = self.mouseSpeed
        self.mouseSpeed = 0.1

        # Sell all from bench
        for i in range(9):
            self.sell_from_bench(i)
        # Sell all from board
        for i in range(4):
            for j in range(7):
                self.sell_from_board([i, j])

        self.mouseSpeed = initial_mouse_speed

    def wait(self):
        time.sleep(self.fetchTimer())



