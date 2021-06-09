# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
import PIL.ImageOps
import pytesseract      # Image interpreter
import pyautogui        # Screen manipulation
import time
from acquirer import Acquirer


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
    def __init__(self, maxTime=0.5):
        super().__init__()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # track relevant data on the frame
        w, h = pyautogui.size()  # Get the size of the primary monitor.
        self.screen = {
            "width": w,
            "height": h,
        }
        self.screenshot = {
            "screenshot": pyautogui.screenshot(),
            "timestamp": 0,
        }
        self.maxTime = maxTime

    def fetchStore(self):
        # run tesseract to locate text
        # recognize champs in store
        upperHeightMod = 1041/1080
        lowerHeightMod = 1069/1080
        leftWidthMod = 485/1920
        nameWidthMod = 140/1920
        storeWidthMod = 201/1920
        x = self.screen['width']*leftWidthMod
        store = [None] * 5
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
            store[i] = name if name != "" else None
            x += self.screen['width'] * storeWidthMod
        return store

    def fetchLevel(self):
        # see  level
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
        str_gold = read(ss, whitelist="0123456789")
        if len(str_gold) < 1:
            str_gold = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            return int(str_gold)
        except:
            return 0

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
        str_gold = read(ss, whitelist="0123456789")
        if len(str_gold) < 1:
            str_gold = pytesseract.image_to_string(ss,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            return int(str_gold)
        except:
            return 0

    # main function: reads data from in-game screenshot
    def refresh(self):
        """
        Refresh screenshot if old enough.
        Defined by self.maxTime.
        """
        now = time.time()
        if now - self.screenshot["timestamp"] > self.maxTime:
            self.screenshot = {
                "screenshot": pyautogui.screenshot(),
                "timestamp": now,
            }

    def getStore(self):
        self.refresh()
        return self.fetchStore()

    def getLevel(self):
        self.refresh()
        return self.fetchLevel()

    def getGold(self):
        self.refresh()
        return self.fetchGold()

    def getXpToLevelUp(self):
        return 0

    def getHp(self):
        return 0
