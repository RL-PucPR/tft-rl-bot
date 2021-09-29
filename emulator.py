from acquirer import Acquirer


def swap(a, b):
    return b, a


class Emulator(Acquirer):
    def __init__(self, database, controller):
        super().__init__(database)
        self.controller = controller

    def buy_champion(self, position):
        if self.gold < self.store[position]["price"]:
            return self.rewardValues["rejected"]
        self.gold -= self.store[position]["price"]
        return self.__champ_bought(self.store[position]["name"])

    def move_from_bench_to_board(self, start, end):
        if self.bench[start] is None:
            return self.rewardValues["rejected"]
        if self.board[end[0]][end[1]] is None and not self.champsOnBoard < self.level:
            return self.rewardValues["rejected"]
        new = self.bench[start]
        old = self.board[end[0]][end[1]]
        if old is None:
            # Champion was added
            return self.rewardValues["add_champ_" + str(new["star"])]
        else:
            # Champions swapped
            if new["star"] == old["star"]:
                # Same level champions
                return self.rewardValues["simple_swap"]
            else:
                return self.rewardValues["swap_" + str(old["star"]) + "-" + str(new["star"])]

    def move_from_board_to_bench(self, start, end):
        if self.board[start[0]][start[1]] is None:
            return self.rewardValues["rejected"]
        new = self.board[start[0]][start[1]]
        old = self.bench[end]
        if old is None:
            # Champion was removed
            self.champsOnBoard -= 1
            return self.rewardValues["remove_champ_" + str(new["star"])]
        else:
            # Champions swapped
            if new["star"] == old["star"]:
                # Same level champions
                return self.rewardValues["simple_swap"]
            else:
                return self.rewardValues["swap_" + str(new["star"]) + "-" + str(old["star"])]

    def move_in_bench(self, start, end):
        if self.bench[start] is None:
            return self.rewardValues["rejected"]
        aux = self.bench[start]
        self.bench[start] = self.bench[end]
        self.bench[end] = aux
        return self.rewardValues["simple_swap"]

    def move_in_board(self, start, end):
        if self.board[start[0]][start[1]] is None:
            return self.rewardValues["rejected"]
        aux = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = aux
        return self.rewardValues["simple_swap"]

    def sell_from_bench(self, position):
        if self.bench[position] is None:
            return self.rewardValues["rejected"]
        sold = self.bench[position]
        self.bench[position] = None
        self.gold += self.controller.sell_champ(sold)
        return self.rewardValues["sell_" + str(sold["star"])]

    def sell_from_board(self, position):
        if self.board[position[0]][position[1]] is None:
            return self.rewardValues["rejected"]
        sold = self.board[position[0]][position[1]]
        self.board[position[0]][position[1]] = None
        self.champsOnBoard -= 1
        self.gold += self.controller.sell_champ(sold)
        return self.rewardValues["sell_" + str(sold["star"])]

    def buy_exp(self):
        if self.gold < 4:
            return self.rewardValues["rejected"]
        old_level = self.level
        self.level, self.xp = self.controller.buy_exp(self.level, self.xp)
        if old_level < self.level:
            return self.rewardValues["level_up"]
        else:
            return self.rewardValues["xp_buy"]

    def refresh_store(self):
        if self.gold < 2:
            return self.rewardValues["rejected"]
        self.store = self.controller.refresh_shop(self.store, self.level, self.gold)
        self.gold -= 2
        return self.rewardValues["rerolled"]

    def wait(self):
        self.controller.wait(self)
        return self.rewardValues["basic"]

    def clear_board(self):
        self.bench = [None] * 9
        self.board = [[None] * 7 for _ in range(4)]
        self.champsOnBoard = 0
