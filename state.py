
class GameState:
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

    # TODO - define getters to be called by player

    def getGold(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["gold"]

    def getStore(self):
        """
        Returns array containing champions found in store (use after retrieval).
        """
        return self.data["store"]

    def update(self):
        # TODO - all getters from acquirer
        self.data["gold"] = self.acquirer.getGold()

    def apply(self, func, *args, **kwargs):
        # TODO - I want to do some actions in gamestate (like buying from the store)
        self.acquirer.func(args, kwargs)
        self.update()

    def __init__(self, acquirer):
        self.acquirer = acquirer


