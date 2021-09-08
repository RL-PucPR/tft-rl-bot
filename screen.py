# Source: https://raw.githubusercontent.com/chris8736/tft-ai/master/ScreenInterpreter.py

from PIL import Image
import PIL.ImageOps
import pytesseract  # Image interpreter
import pyautogui  # Screen manipulation
import time
from acquirer import Acquirer
from database import DDragon


def read(img, blacklist=".,_-~()", whitelist=None):
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
    def __init__(self, database, max_time=2, keyboard=False, speed=0.1):
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
        self.board = [[None] * 7 for _ in range(4)]
        self.store = [None] * 5
        self.champsOnBoard = 0
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
        self.requiredExp = database.requiredExp
        self.championPrices = database.championPrices
        self.rewardValues = database.rewardValues
        self.useKeyboard = keyboard
        self.mouseSpeed = speed
        self.nextFunction = None
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
    # Champion positions always prioritize leftmost and lowermost (for board)
    # Bench positions are arrays of len == 1 and board are of len == 2
    def __next_bench_available(self):
        for i in range(len(self.bench)):
            if self.bench[i] is None:
                return [i]

    def __next_board_available(self):
        for i in range(len(self.board)):
            for j in range(len((self.board[i]))):
                if self.board[i][j] is None:
                    return [i, j]

    def __next_available(self):
        # Next available prioritize bench over board
        pos = self.__next_bench_available()
        if pos is not None:
            return pos

        return self.__next_board_available()

    def __can_merge(self, champion_pos):
        # Returns the list of positions of the champions that would be merged
        if len(champion_pos) > 1:
            champion = self.board[champion_pos[0]][champion_pos[1]]
        else:
            champion = self.bench[champion_pos[0]]
        positions = []
        for i in range(len(self.board)):
            for j in range(len((self.board[i]))):
                if is_same_champ(self.board[i][j], champion):
                    positions.append([i, j])
                    if len(positions) == 3:
                        return positions
        for i in range(len(self.bench)):
            if is_same_champ(self.bench[i], champion):
                positions.append([i])
                if len(positions) == 3:
                    return positions
        # Champion is not able to be merged
        return False

    def __merge(self, pos_list):
        # Merging prioritize board over bench
        # pos_list parameter is already ordered following priority
        pos = pos_list[0]
        if len(pos) > 1:
            self.board[pos[0]][pos[1]]["star"] += 1
        else:
            self.bench[pos[0]]["star"] += 1

        for aux in pos_list[1:]:
            if len(aux) > 1:
                self.board[aux[0]][aux[1]] = None
                self.champsOnBoard -= 1
            else:
                self.bench[aux[0]] = None

        return pos

    def __champ_bought(self, champion_name):
        pos = self.__next_available()
        champion = {
            "name": champion_name,
            "star": 1
        }
        if len(pos) > 1:
            self.board[pos[0]][pos[1]] = champion
        else:
            self.bench[pos[0]] = champion
        pos_list = self.__can_merge(pos)
        if pos_list:
            pos = self.__merge(pos_list)
            pos_list = self.__can_merge(pos)
            if pos_list:
                self.__merge(pos_list)
                return self.rewardValues["combine_3"]
            return self.rewardValues["combine_2"]
        return self.rewardValues["simple_buy"]

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
            self.store[i] = {"name": name, "price": self.championPrices[name]} if name in self.championPrices else None
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
        # TODO - Implement check for 1-? stages (different coordinates)
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
        # recognize current stage
        # TODO - Implement check for 1-? stages (different coordinates)
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
            if stage[1] == 4:
                self.nextFunction = self.wait
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
            "board": self.board,
            "bench": self.bench,
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
    def fill_board(self):
        while self.champsOnBoard < self.level:
            pos = self.__next_board_available()
            for i in range(len(self.bench)):
                if self.bench[i] is not None:
                    self.move_from_bench_to_board(i, pos)
                    break
            else:
                return

    def buy_champion(self, position):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.store[position] is None:
            return self.rewardValues["rejected"]
        if None not in self.bench:
            return self.rewardValues["rejected"]
        if self.gold < self.store[position]["price"]:
            return self.rewardValues["rejected"]
        base_width = 575
        height = 995
        modifier = 200
        pyautogui.moveTo(base_width + modifier * position, height, duration=self.mouseSpeed)
        left_click()
        reward = self.__champ_bought(self.store[position]["name"])
        self.store[position] = None
        if self.champsOnBoard < self.level and sum(x is not None for x in self.bench) > 0:
            self.nextFunction = self.move_from_bench_to_board
        return reward

    def __to_bench(self, action, position):
        base_width = 425
        height = 777
        modifier = 118
        action(base_width + modifier * position, height, duration=self.mouseSpeed)

    def __to_board(self, action, position):
        if position[0] == 3:
            base_width = 575
            height = 675
            modifier = 130
        elif position[0] == 2:
            base_width = 530
            height = 590
            modifier = 125
        elif position[0] == 1:
            base_width = 605
            height = 510
            modifier = 120
        elif position[0] == 0:
            base_width = 560
            height = 440
            modifier = 115
        else:
            return

        action(base_width + modifier * position[1], height, duration=self.mouseSpeed)

    def move_from_bench_to_board(self, start, end):
        if self.nextFunction is not None or self.nextFunction != self.move_from_bench_to_board:
            return self.rewardValues["rejected"]
        if self.bench[start] is None:
            return self.rewardValues["rejected"]
        if self.board[end[0]][end[1]] is None and not self.champsOnBoard < self.level:
            return self.rewardValues["rejected"]
        self.nextFunction = None

        new = self.bench[start]
        old = self.board[end[0]][end[1]]
        self.__to_bench(pyautogui.moveTo, start)
        self.__to_board(pyautogui.dragTo, end)
        self.bench[start] = old
        self.board[end[0]][end[1]] = new
        self.champsOnBoard += 1

        if self.champsOnBoard < self.level and sum(x is not None for x in self.bench) > 0:
            self.nextFunction = self.move_from_bench_to_board

        if old is None:
            # Champion was added
            return self.rewardValues["add_champ_"+str(new["star"])]
        else:
            # Champions swapped
            if new["star"] == old["star"]:
                # Same level champions
                return self.rewardValues["simple_swap"]
            else:
                return self.rewardValues["swap_"+str(old["star"])+"-"+str(new["star"])]

    def move_from_board_to_bench(self, start, end):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.board[start[0]][start[1]] is None:
            return self.rewardValues["rejected"]

        new = self.board[start[0]][start[1]]
        old = self.bench[end]
        self.__to_board(pyautogui.moveTo, start)
        self.__to_bench(pyautogui.dragTo, end)
        self.board[start[0]][start[1]] = old
        self.bench[end] = new

        if old is None:
            # Champion was removed
            self.champsOnBoard -= 1
            if self.champsOnBoard < self.level and sum(x is not None for x in self.bench) > 0:
                self.nextFunction = self.move_from_bench_to_board
            return self.rewardValues["remove_champ_"+str(new["star"])]
        else:
            # Champions swapped
            if new["star"] == old["star"]:
                # Same level champions
                return self.rewardValues["simple_swap"]
            else:
                return self.rewardValues["swap_"+str(new["star"])+"-"+str(old["star"])]

    def move_in_bench(self, start, end):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.bench[start] is None:
            return self.rewardValues["rejected"]
        self.__to_bench(pyautogui.moveTo, start)
        self.__to_bench(pyautogui.dragTo, end)
        aux = self.bench[start]
        self.bench[start] = self.bench[end]
        self.bench[end] = aux
        return self.rewardValues["simple_swap"]

    def move_in_board(self, start, end):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.board[start[0]][start[1]] is None:
            return self.rewardValues["rejected"]
        self.__to_board(pyautogui.moveTo, start)
        self.__to_board(pyautogui.dragTo, end)
        aux = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = aux
        return self.rewardValues["simple_swap"]

    def sell_from_bench(self, position):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.bench[position] is None:
            return self.rewardValues["rejected"]
        self.__to_bench(pyautogui.moveTo, position)
        if self.useKeyboard:
            pyautogui.press("e")
        else:
            pyautogui.dragTo(900, 1000, duration=self.mouseSpeed)
        sold = self.bench[position]
        self.bench[position] = None
        return self.rewardValues["sell_"+str(sold["star"])]

    def sell_from_board(self, position):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.board[position[0]][position[1]] is None:
            return self.rewardValues["rejected"]
        self.__to_board(pyautogui.moveTo, position)
        if self.useKeyboard:
            pyautogui.press("e")
        else:
            pyautogui.dragTo(900, 1000, duration=self.mouseSpeed)
        sold = self.board[position[0]][position[1]]
        self.board[position[0]][position[1]] = None
        self.champsOnBoard -= 1
        if self.champsOnBoard < self.level and sum(x is not None for x in self.bench) > 0:
            self.nextFunction = self.move_from_bench_to_board
        return self.rewardValues["sell_"+str(sold["star"])]

    def buy_exp(self):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.gold < 4:
            return self.rewardValues["rejected"]
        if self.useKeyboard:
            pyautogui.press("f")
        else:
            pyautogui.moveTo(370, 960, duration=self.mouseSpeed)
            left_click()
        self.refresh()
        old_level = self.level
        self.__fetch_level()
        if self.champsOnBoard < self.level and sum(x is not None for x in self.bench) > 0:
            self.nextFunction = self.move_from_bench_to_board
        if old_level < self.level:
            return self.rewardValues["level_up"]
        else:
            return self.rewardValues["xp_buy"]

    def refresh_store(self):
        if self.nextFunction is not None:
            return self.rewardValues["rejected"]
        if self.gold < 2:
            return self.rewardValues["rejected"]
        if self.useKeyboard:
            pyautogui.press("d")
        else:
            pyautogui.moveTo(360, 1030, duration=self.mouseSpeed)
            left_click()
        return self.rewardValues["rerolled"]

    def wait(self):
        # TODO - add timer check for every move
        if self.nextFunction is not None or self.nextFunction != self.wait:
            return self.rewardValues["rejected"]
        self.nextFunction = None
        old_stage = self.stage
        while old_stage == self.stage:
            time.sleep(self.maxTime)
            self.refresh()
            self.__fetch_stage()
        self.__fetch_level()
        if self.champsOnBoard < self.level and sum(x is not None for x in self.bench) > 0:
            self.nextFunction = self.move_from_bench_to_board
        return self.rewardValues["basic"]

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
