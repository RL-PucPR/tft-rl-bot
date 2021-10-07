from acquirer import Acquirer


class Emulator(Acquirer):
    def __init__(self, database, controller):
        super().__init__(database)
        self.controller = controller

    def buy_champion(self, position):
        if self.store[position] is None:
            return self.rewardValues["rejected"]
        if self.gold < self.store[position]["price"]:
            return self.rewardValues["rejected"]
        if len(list(filter(lambda x: x is None, self.bench))) == 0:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        self.gold -= self.store[position]["price"]
        champion = self.store[position]["name"]
        self.store[position] = None
        return self.champ_bought(champion)

    def move_from_bench_to_board(self, start, end):
        if self.bench[start] is None:
            return self.rewardValues["rejected"]
        if self.board[end[0]][end[1]] is None and not self.champsOnBoard < self.level:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        new = self.bench[start]
        old = self.board[end[0]][end[1]]
        self.bench[start] = old
        self.board[end[0]][end[1]] = new
        if old is None:
            # Champion was added
            self.champsOnBoard += 1
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
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        new = self.board[start[0]][start[1]]
        old = self.bench[end]
        self.board[start[0]][start[1]] = old
        self.bench[end] = new
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
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        aux = self.bench[start]
        self.bench[start] = self.bench[end]
        self.bench[end] = aux
        return self.rewardValues["simple_swap"]

    def move_in_board(self, start, end):
        if self.board[start[0]][start[1]] is None:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        aux = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = aux
        return self.rewardValues["simple_swap"]

    def sell_from_bench(self, position):
        if self.bench[position] is None:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        sold = self.bench[position]
        self.bench[position] = None
        self.gold += self.controller.sell_champ(sold)
        return self.rewardValues["sell_" + str(sold["star"])]

    def sell_from_board(self, position):
        if self.board[position[0]][position[1]] is None:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        sold = self.board[position[0]][position[1]]
        self.board[position[0]][position[1]] = None
        self.champsOnBoard -= 1
        self.gold += self.controller.sell_champ(sold)
        return self.rewardValues["sell_" + str(sold["star"])]

    def buy_exp(self):
        if self.level == 9:
            return self.rewardValues["rejected"]
        if self.gold < 4:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        old_level = self.level
        self.level, self.xp = self.controller.buy_exp(self.level, self.xp)
        if old_level < self.level:
            return self.rewardValues["level_up"]
        else:
            return self.rewardValues["xp_buy"]

    def refresh_store(self):
        if self.gold < 2:
            return self.rewardValues["rejected"]
        self.timer -= 1
        if self.timer < 0:
            self.wait()
        self.store = self.controller.refresh_shop(self.store, self.level)
        self.gold -= 2
        return self.rewardValues["rerolled"]

    def wait(self):
        self.controller.wait(self)
        if self.done and self.position == 0:
            return self.rewardValues["winner"]
        return self.rewardValues["basic"]

    def reset(self):
        self.level = 1
        for i in range(4):
            for j in range(7):
                self.sell_from_board([i, j])
        for i in range(9):
            self.sell_from_bench(i)
        self.store = self.controller.refresh_shop(self.store, self.level)
        self.gold = 0
        self.xp = {
            "actual": 0,
            "required": 1,
        }
        self.hpList = [100] * 8
        self.position = 7
        self.timer = 0
        self.stage = [1, 1]
        self.done = False
