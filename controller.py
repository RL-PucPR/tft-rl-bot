

class Controller:

    # Format:
    # pool = {
    #     cost: [champion, champion]
    # }
    pool = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }

    def __init__(self, database):
        for champion in database.champions:
            self.pool[champion["cost"]].append(champion)
