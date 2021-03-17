# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
import PIL.ImageOps
import pytesseract
import pyautogui


class ScreenInterpreter:
    # ScreenInterpreter will only work with the game running in fullscreen

    # constructor
    def __init__(self):
        # track relevant data on the frame
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        w, h = pyautogui.size()  # Get the size of the primary monitor.
        self.screen = {
            "width": w,
            "height": h,
        }
        self.data = {
            "board": [],
            "store": [None] * 5,
            "gold": 0,
            "level": 0,
            "xp": 0,
            "win_streak": 0,
            "items": {
                "chain_vest": 0,
                "negatron_cloak": 0,
                "needlessly_large_rod": 0,
                "bf_sword": 0,
                "recurve_bow": 0,
                "golden_spatula": 0,
            },
        }

    def updateStore(self, screenshot):
        upperHeightMod = 1041/1080
        lowerHeightMod = 1069/1080
        leftWidthMod = 485/1920
        nameWidthMod = 140/1920
        storeWidthMod = 201/1920
        x = self.screen['width']*leftWidthMod
        for i in range(5):
            name = self.read(
                self.cropAndEdit(
                    screenshot,
                    x,
                    self.screen['height'] * upperHeightMod,
                    x + self.screen['width'] * nameWidthMod,
                    self.screen['height'] * lowerHeightMod
                )
            ).replace("\x0c", "").replace("\n", "").replace(" ", "")
            self.data["store"][i] = name if name == "" else None
            x += self.screen['width'] * storeWidthMod

    def updateGold(self, screenshot):
        upperHeightMod = 881/1080
        lowerHeightMod = 910/1080
        leftWidthMod = 872/1920
        rightWidthMod = 906/1920
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        screenshot = (
            self.cropAndEdit(
                screenshot,
                self.screen['width'] * leftWidthMod,
                self.screen['height'] * upperHeightMod,
                self.screen['width'] * rightWidthMod,
                self.screen['height'] * lowerHeightMod
            )
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        str_gold = self.read(screenshot, whitelist="0123456789")
        if len(str_gold) < 1:
            str_gold = pytesseract.image_to_string(screenshot,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789")
        try:
            self.data["gold"] = int(str_gold)
        except:
            self.data["gold"] = 0

    # main function: reads data from in-game screenshot
    def retrieveData(self, screenshot):
        """
        Retrieves relevant data (e.g. champs, gold, items, etc.) from the latest screenshot.
        """
        # run tesseract to locate text
        # recognize champs in store and on board
        # see gold
        # if champ info open, record
        self.updateStore(screenshot)

        self.updateGold(screenshot)


    def cropAndEdit(self, img, x1, y1, x2, y2):
        """
        Crops, inverts, and desaturates image.
        """
        img1 = PIL.ImageOps.invert(img.crop((x1, y1, x2, y2)))
        img1 = img1.convert("LA")
        img1.save("tmp/out.png")
        return img1

    def read(self, img, blacklist=".,", whitelist=None):
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

    def getStore(self):
        """
        Returns array containing champions found in store (use after retrieval).
        """
        return self.data["store"]

    def getGold(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["gold"]
