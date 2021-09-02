# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
import PIL.ImageOps
import pytesseract  # Image interpreter
import pyautogui  # Screen manipulation
import time
from acquirer import Acquirer
from database import requiredExp


def read(img, blacklist=".,", whitelist=None):
    """
    Performs the tesseract operation on a cropped image after inversion and desaturation.
    """
    if whitelist:
        return pytesseract.image_to_string(
            img, config="--psm 6 -c tessedit_char_whitelist=" + whitelist
        )
    else:
        return pytesseract.image_to_string(
            img, config="--psm 6 -c tessedit_char_blacklist=" + blacklist
        )


def crop_and_edit(img, x1, y1, x2, y2):
    """
    Crops, inverts, and desaturates image.
    """
    img1 = PIL.ImageOps.invert(img.crop((x1, y1, x2, y2)))
    img1 = img1.convert("LA")
    img1.save("tmp/out.png")
    return img1


def left_click(delay=0.1):
    pyautogui.mouseDown()
    time.sleep(delay)
    pyautogui.mouseUp()


def is_same_champ(a, b):
    return a is not None and b is not None and a["name"] == b["name"] and a["star"] == b["star"]


class ScreenInterpreter:
    # ScreenInterpreter will only work with the game running in fullscreen

    # constructor
    def __init__(self, max_time=2, keyboard=False, speed=0.1):
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
        self.maxTime = max_time
        self.bench = [None] * 9
        self.board = [[None] * 7] * 4
        self.store = [None] * 5
        self.level = 1
        self.gold = 0
        self.xp = {
            "actual": 0,
            "required": 0,
        }
        self.hpList = [100] * 8
        self.position = 7
        self.timer = 0
        self.stage = [0, 0]
        self.done = False
        self.lock = False
        self.requiredExp = requiredExp()
        self.useKeyboard = keyboard
        self.mouseSpeed = speed
        self.fetchFunctions = [
            self.__fetch_store,
            self.__fetch_level,
            self.__fetch_gold,
            self.__fetch_exp,
            self.__fetch_hp,
            self.__fetch_timer,
            self.__fetch_stage,
        ]

    # Functions destined to control champion position
    def __next_available(self):
        # TODO - Check position priorities
        for i in range(len(self.bench)):
            if self.bench[i] is None:
                return i
        for i in range(len(self.board)):
            for j in range(len((self.board[i]))):
                if self.board[i][j] is None:
                    return [i, j]

    def __can_merge(self, champion_pos):
        if isinstance(champion_pos, type([])):
            champion = self.board[champion_pos[0]][champion_pos[1]]
        else:
            champion = self.bench[champion_pos]
        positions = [champion_pos]
        for i in range(len(self.bench)):
            if is_same_champ(self.bench[i], champion):
                positions.append(i)
                if len(positions) == 3:
                    return positions
        for i in range(len(self.board)):
            for j in range(len((self.board[i]))):
                if is_same_champ(self.board[i][j], champion):
                    positions.append([i, j])
                    if len(positions) == 3:
                        return positions
        return positions

    def __merge(self, pos_list):
        # TODO - Check position priorities
        pos = 0
        return pos

    def __champ_bought(self, champion_name):
        pos = self.__next_available()
        champion = {
            "name": champion_name,
            "star": 1
        }
        if isinstance(pos, type([])):
            self.board[pos[0]][pos[1]] = champion
        else:
            self.bench[pos] = champion
        pos_list = self.__can_merge(pos)
        if len(pos_list) == 3:
            pos = self.__merge(pos_list)
            pos_list = self.__can_merge(pos)
            if len(pos_list) == 3:
                pos = self.__merge(pos_list)

    [{"name": "Leona", "star": 1}, None, None, None, None, None, None, None, None]

    # Internal functions - called after refresh
    def __fetch_store(self):
        # run tesseract to locate text
        # recognize champs in store
        upper_height_mod = 1041 / 1080
        lower_height_mod = 1069 / 1080
        left_width_mod = 485 / 1920
        name_width_mod = 140 / 1920
        store_width_mod = 201 / 1920
        x = self.screen['width'] * left_width_mod
        for i in range(5):
            name = read(
                crop_and_edit(
                    self.screenshot["screenshot"],
                    x,
                    self.screen['height'] * upper_height_mod,
                    x + self.screen['width'] * name_width_mod,
                    self.screen['height'] * lower_height_mod
                )
            ).replace("\x0c", "").replace("\n", "")
            self.store[i] = name if name != "" else None
            x += self.screen['width'] * store_width_mod

    def __fetch_level(self):
        # run tesseract to locate text
        # recognize player  level
        upper_height_mod = 880 / 1080
        lower_height_mod = 908 / 1080
        left_width_mod = 314 / 1920
        right_width_mod = 345 / 1920
        ss = (
            crop_and_edit(
                self.screenshot["screenshot"],
                self.screen['width'] * left_width_mod,
                self.screen['height'] * upper_height_mod,
                self.screen['width'] * right_width_mod,
                self.screen['height'] * lower_height_mod
            )
                .resize((200, 200), Image.ANTIALIAS)
                .convert("L")
                .point(lambda x: 255 if x > 150 else 0, mode="1")
        )
        str_level = read(ss, whitelist="0123456789")
        try:
            self.level = int(str_level)
        except:
            pass

    def __fetch_gold(self):
        # run tesseract to locate text
        # recognize player gold
        upper_height_mod = 881 / 1080
        lower_height_mod = 910 / 1080
        left_width_mod = 872 / 1920
        right_width_mod = 906 / 1920
        ss = (
            crop_and_edit(
                self.screenshot["screenshot"],
                self.screen['width'] * left_width_mod,
                self.screen['height'] * upper_height_mod,
                self.screen['width'] * right_width_mod,
                self.screen['height'] * lower_height_mod
            )
                .resize((200, 200), Image.ANTIALIAS)
                .convert("L")
                .point(lambda x: 255 if x > 150 else 0, mode="1")
        )
        str_gold = read(ss, whitelist="0123456789")
        try:
            self.gold = int(str_gold)
        except:
            pass

    def __fetch_timer(self):
        # run tesseract to locate text
        # recognize turn timer
        upper_height_mod = 10 / 1080
        lower_height_mod = 32 / 1080
        left_width_mod = 1142 / 1920
        right_width_mod = 1172 / 1920
        ss = (
            crop_and_edit(
                self.screenshot["screenshot"],
                self.screen['width'] * left_width_mod,
                self.screen['height'] * upper_height_mod,
                self.screen['width'] * right_width_mod,
                self.screen['height'] * lower_height_mod
            )
                .resize((200, 200), Image.ANTIALIAS)
                .convert("L")
                .point(lambda x: 255 if x > 150 else 0, mode="1")
        )
        str_timer = read(ss, whitelist="0123456789")
        try:
            self.timer = int(str_timer)
        except:
            self.timer = 0

    def __fetch_exp(self):
        # run tesseract to locate text
        # recognize player experience
        upper_height_mod = 882 / 1080
        lower_height_mod = 908 / 1080
        if self.requiredExp[self.level] < 10:
            left_width_mod = 410 / 1920
            right_width_mod = 432 / 1920
        else:
            left_width_mod = 405 / 1920
            right_width_mod = 425 / 1920
        ss = (
            crop_and_edit(
                self.screenshot["screenshot"],
                self.screen['width'] * left_width_mod,
                self.screen['height'] * upper_height_mod,
                self.screen['width'] * right_width_mod,
                self.screen['height'] * lower_height_mod
            )
                .resize((200, 200), Image.ANTIALIAS)
                .convert("L")
                .point(lambda x: 255 if x > 150 else 0, mode="1")
        )
        str_exp = read(ss, whitelist="0123456789")
        try:
            self.xp["actual"] = int(str_exp)
            if self.xp["actual"] >= self.xp["required"]:
                self.xp["actual"] = 0
        except:
            pass

    def __fetch_hp(self):
        # run tesseract to locate text
        # recognize player current hp and position
        upper_height_mod = 207 / 1080
        left_width_mod = 1775 / 1920
        right_width_mod = 1827 / 1920
        opp_left_width_mod = 1823 / 1920
        opp_right_width_mod = 1847 / 1920
        hp_height_mod = 35 / 1080
        player_height_mod = 72 / 1080
        x = self.screen['height'] * upper_height_mod
        for i in range(8):
            # Check for opponent's hp
            ss = (
                crop_and_edit(
                    self.screenshot["screenshot"],
                    self.screen['width'] * opp_left_width_mod,
                    x,
                    self.screen['width'] * opp_right_width_mod,
                    x + self.screen['height'] * hp_height_mod
                )
                    .resize((200, 200), Image.ANTIALIAS)
                    .convert("L")
                    .point(lambda a: 255 if a > 150 else 0, mode="1")
            )
            str_hp = read(ss, whitelist="0123456789")
            try:
                int_hp = int(str_hp)
                if int_hp <= 100:
                    self.hpList[i] = int_hp
                    if int_hp == 0 and self.position < i:
                        if self.position == 0 and self.position == i - 1:
                            self.done = True
                        return
            except:
                # If no number was found, check for your hp
                ss = (
                    crop_and_edit(
                        self.screenshot["screenshot"],
                        self.screen['width'] * left_width_mod,
                        x,
                        self.screen['width'] * right_width_mod,
                        x + self.screen['height'] * hp_height_mod
                    )
                        .resize((200, 200), Image.ANTIALIAS)
                        .convert("L")
                        .point(lambda a: 255 if a > 150 else 0, mode="1")
                )
                str_hp = read(ss, whitelist="0123456789")
                try:
                    int_hp = int(str_hp)
                    if int_hp <= 100:
                        self.hpList[i] = int_hp
                        self.position = i
                        if int_hp == 0:
                            self.done = True
                            return
                except:
                    pass
            x += self.screen['height'] * player_height_mod

    def __fetch_stage(self):
        # run tesseract to locate text
        # recognize champs in store
        upper_height_mod = 10 / 1080
        lower_height_mod = 30 / 1080
        left_width_mod = 770 / 1920
        right_width_mod = 810 / 1920
        ss = (
            crop_and_edit(
                self.screenshot["screenshot"],
                self.screen['width'] * left_width_mod,
                self.screen['height'] * upper_height_mod,
                self.screen['width'] * right_width_mod,
                self.screen['height'] * lower_height_mod
            )
                .resize((200, 200), Image.ANTIALIAS)
                .convert("L")
                .point(lambda a: 255 if a > 150 else 0, mode="1")
        )
        stage = read(ss, whitelist="0123456789-")
        try:
            self.stage = [int(n) for n in stage.split("-")]
            if len(self.stage) == 1:
                self.stage = [
                    int(self.stage[0] / 10),
                    self.stage[0] % 10
                ]
        except:
            self.stage = [0, 0]

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
            "timer": self.timer,
            "stage": self.stage,
            "done": self.done
        }

    # Setters
    def can_perform_action(self):
        if self.stage[1] == 4:  # Stages ?-4 are carousel
            self.lock = True
            return False
        self.__fetch_timer()
        if self.timer < self.maxTime:
            self.lock = True
        if self.lock:
            return False
        return True

    def buy_champion(self, position):
        base_width = 575
        height = 995
        modifier = 200
        pyautogui.moveTo(base_width + modifier * position, height, duration=self.mouseSpeed)
        left_click()

    def __to_bench(self, action, position):
        base_width = 425
        height = 777
        modifier = 118
        action(base_width + modifier * position, height, duration=self.mouseSpeed)

    def __to_board(self, action, position):
        if position[0] == 0:
            base_width = 575
            height = 675
            modifier = 130
        elif position[0] == 1:
            base_width = 530
            height = 590
            modifier = 125
        elif position[0] == 2:
            base_width = 605
            height = 510
            modifier = 120
        elif position[0] == 3:
            base_width = 560
            height = 440
            modifier = 115
        else:
            return

        action(base_width + modifier * position[1], height, duration=self.mouseSpeed)

    def move_from_bench_to_board(self, start, end):
        self.__to_bench(pyautogui.moveTo, start)
        self.__to_board(pyautogui.dragTo, end)

    def move_from_board_to_bench(self, start, end):
        self.__to_board(pyautogui.moveTo, start)
        self.__to_bench(pyautogui.dragTo, end)

    def move_in_bench(self, start, end):
        self.__to_bench(pyautogui.moveTo, start)
        self.__to_bench(pyautogui.dragTo, end)

    def move_in_board(self, start, end):
        self.__to_board(pyautogui.moveTo, start)
        self.__to_board(pyautogui.dragTo, end)

    def sell_from_bench(self, position):
        self.__to_bench(pyautogui.moveTo, position)
        if self.useKeyboard:
            pyautogui.press("e")
        else:
            pyautogui.dragTo(900, 1000, duration=self.mouseSpeed)

    def sell_from_board(self, position):
        self.__to_board(pyautogui.moveTo, position)
        if self.useKeyboard:
            pyautogui.press("e")
        else:
            pyautogui.dragTo(900, 1000, duration=self.mouseSpeed)

    def buy_exp(self):
        if self.useKeyboard:
            pyautogui.press("f")
        else:
            pyautogui.moveTo(370, 960, duration=self.mouseSpeed)
            left_click()

    def refresh_store(self):
        if self.useKeyboard:
            pyautogui.press("d")
        else:
            pyautogui.moveTo(360, 1030, duration=self.mouseSpeed)
            left_click()

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
        old_stage = self.stage
        while old_stage == self.stage:
            # time.sleep(self.__fetch_timer())
            time.sleep(self.maxTime)
            self.refresh()
            self.__fetch_stage()
