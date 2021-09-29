import random


class Battler:
    championInfo = {}

    def battle(self, board, opp=None):
        # If opp is not None, it is a dummy from the controller, get board
        # If opp is None, await for another battle call and use both as opponents
        if opp is None:
            raise NotImplementedError
        else:
            opp_board = opp.board
        return 1

    def __init__(self, database):
        for champion in database.champions:
            self.championInfo[champion["name"]] = champion
