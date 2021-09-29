import random


class Battler:
    championInfo = {}

    def battle(self, board, opp=None):
        # If opp is not None, it is a dummy from the controller, get board
        # If opp is None, await for another battle call and use both as opponents
        if opp is None:
            raise NotImplementedError
        else:
            # If result == 0 -> Draw
            # If result > 0 -> Win
            # If result < 0 -> Loss
            result = 0
            opp_board = opp.board
            for i in range(len(board)):
                for j in range(len(board[i])):
                    if board[i][j] is not None:
                        result += board[i][j]["star"]
                    if opp_board[i][j] is not None:
                        result -= opp_board[i][j]["star"]
            return result

    def __init__(self, database):
        for champion in database.champions:
            self.championInfo[champion["name"]] = champion
