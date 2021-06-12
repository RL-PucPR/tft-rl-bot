# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
import PIL.ImageOps
import pytesseract      # Image interpreter
import pyautogui        # Screen manipulation
import time
from acquirer import Acquirer
from database import requiredXp


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


class ScreenInterpreter(Acquirer):
    # ScreenInterpreter will only work with the game running in fullscreen

    # constructor
    def __init__(self, maxTime=2):
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
        self.hp = 100
        self.requiredXp = requiredXp()

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
            return

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
            self.gold = 0

    def fetchXp(self):
        # run tesseract to locate text
        # recognize champs in store
        upperHeightMod = 882/1080
        lowerHeightMod = 908/1080
        if self.requiredXp[self.level] < 10:
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
        strXp = read(ss, whitelist="0123456789")
        if len(strXp) < 1:
            strXp = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            self.xp["actual"] = int(strXp)
            if self.xp["actual"] >= self.xp["required"]:
                self.xp["actual"] = 0
        except:
            self.xp["actual"] = 0

    def fetchHp(self):
        upperHeightMod = 207/1080
        leftWidthMod = 1775/1920
        rightWidthMod = 1827/1920
        hpHeightMod = 35/1080
        playerHeightMod = 72/1080
        x = self.screen['height'] * upperHeightMod
        thresh = 150
        fn = lambda a: 255 if a > thresh else 0
        for i in range(8):
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
                    self.hp = intHp
                    return
            except:
                pass
            x += self.screen['height'] * playerHeightMod
        self.hp = 0

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
            self.fetchStore()
            self.fetchLevel()
            self.fetchGold()
            self.fetchXp()
            self.fetchHp()

    def getStore(self):
        self.refresh()
        return self.store

    def getLevel(self):
        self.refresh()
        return self.level

    def getGold(self):
        self.refresh()
        return self.gold

    def getXpToLevelUp(self):
        self.refresh()
        return self.xp["required"] - self.xp["actual"]

    def getHp(self):
        self.refresh()
        return self.hp
