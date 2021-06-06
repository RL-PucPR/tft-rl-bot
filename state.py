

class Getters:
    acquirer = None
    data = {
        "champions": [],
        "bench": [None] * 9,
        "board": [[None] * 7] * 3,
        "store": [None] * 5,
        "gold": 0,
        "level": 1,
        "xpToLevelUp": 0,
        "hp": 0,
    }

    def getGold(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["gold"]

    def getLevel(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["level"]

    def getStore(self):
        """
        Returns array containing champions found in store (use after retrieval).
        """
        return self.data["store"]

    def getXpToLevelUp(self):
        """
        Returns the ammount of xp missing for the player to level up (use after retrieval).
        """
        return self.data["xpToLevelUp"]

    def getHp(self):
        """
        Returns current value for the player's hp (use after retrieval).
        """
        return self.data["hp"]

    def update(self):
        self.data["gold"] = self.acquirer.getGold()
        self.data["level"] = self.acquirer.getLevel()
        self.data["store"] = self.acquirer.getStore()
        self.data["xpToLevelUp"] = self.acquirer.getXpToLevelUp()
        self.data["hp"] = self.acquirer.getHp()


class Setters:
    pass


class GameState(Getters, Setters):
    # champion format
    # {
    #     "name": "Vayne",
    #     "star": 2,
    #     "quantity": 1,
    # }
    data = {
        "champions": [],
        "bench": [None] * 9,
        "board": [[None] * 7] * 3,
        "store": [None] * 5,
        "gold": 0,
        "level": 1,
        "xpToLevelUp": 0,
        "hp": 0,
    }

    def apply(self, func, *args, **kwargs):
        # TODO - I want to do some actions in gamestate (like buying from the store)
        self.acquirer.func(args, kwargs)
        self.update()

    def __init__(self, acquirer):
        self.acquirer = acquirer


