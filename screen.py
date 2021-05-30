# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
from controller import Controller
import PIL.ImageOps
import pytesseract
import pyautogui
import time


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


class ScreenInterpreter(Controller):
    # ScreenInterpreter will only work with the game running in fullscreen

    # constructor
    def __init__(self, max_time=5):
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
        self.maxTime = max_time

    def update_store(self):
        # run tesseract to locate text
        # recognize champs in store
        upper_height_mod = 1041 / 1080
        lower_height_mod = 1069 / 1080
        left_width_mod = 485 / 1920
        name_width_mod = 140 / 1920
        store_width_mod = 201 / 1920
        x = self.screen['width'] * left_width_mod
        store = [None] * 5
        for i in range(len(store)):
            name = read(
                cropAndEdit(
                    self.screenshot["screenshot"],
                    x,
                    self.screen['height'] * upper_height_mod,
                    x + self.screen['width'] * name_width_mod,
                    self.screen['height'] * lower_height_mod
                )
            ).replace("\x0c", "").replace("\n", "").replace(" ", "")
            store[i] = name if name == "" else None
            x += self.screen['width'] * store_width_mod
        return store

    def update_gold(self):
        # see gold
        upper_height_mod = 881 / 1080
        lower_height_mod = 910 / 1080
        left_width_mod = 872 / 1920
        right_width_mod = 906 / 1920
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        ss = (
            cropAndEdit(
                self.screenshot["screenshot"],
                self.screen['width'] * left_width_mod,
                self.screen['height'] * upper_height_mod,
                self.screen['width'] * right_width_mod,
                self.screen['height'] * lower_height_mod
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

    def get_store(self):
        self.refresh()
        return self.update_store()

    def get_gold(self):
        self.refresh()
        return self.update_gold()
