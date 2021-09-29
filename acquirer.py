import abc


def is_same_champ(a, b):
    return a is not None and b is not None and a["name"] == b["name"] and a["star"] == b["star"]


class Player(abc.ABC):
    bench = [None] * 9
    board = [[None] * 7 for _ in range(4)]

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


class Acquirer(Player):
    store = [None] * 5
    champsOnBoard = 0
    level = 1
    gold = 0
    xp = {
        "actual": 0,
        "required": 0,
    }
    hpList = [100] * 8
    position = 7
    timer = 0
    stage = [0, 0]
    done = False
    lock = False

    def __init__(self, database):
        self.requiredExp = database.requiredExp
        self.championPrices = database.championPrices
        self.rewardValues = database.rewardValues

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

    def get_observation(self):
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

    @abc.abstractmethod
    def buy_champion(self, position):
        return 0

    @abc.abstractmethod
    def move_from_bench_to_board(self, start, end):
        return 0

    @abc.abstractmethod
    def move_from_board_to_bench(self, start, end):
        return 0

    @abc.abstractmethod
    def move_in_bench(self, start, end):
        return 0

    @abc.abstractmethod
    def move_in_board(self, start, end):
        return 0

    @abc.abstractmethod
    def sell_from_bench(self, position):
        return 0

    @abc.abstractmethod
    def sell_from_board(self, position):
        return 0

    @abc.abstractmethod
    def buy_exp(self):
        return 0

    @abc.abstractmethod
    def refresh_store(self):
        return 0

    @abc.abstractmethod
    def wait(self):
        return 0

    @abc.abstractmethod
    def clear_board(self):
        return 0
