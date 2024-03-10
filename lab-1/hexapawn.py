from easyAI import TwoPlayerGame
import copy
import random
import config
import time
import pandas as pd

# Convert D7 to (3,6) and back...
to_string = lambda move: " ".join(
    ["ABCDEFGHIJ"[move[i][0]] + str(move[i][1] + 1) for i in (0, 1)]
)
to_tuple = lambda s: ("ABCDEFGHIJ".index(s[0]), int(s[1:]) - 1)


class Hexapawn(TwoPlayerGame):
    """
    A nice game whose rules are explained here:
    http://fr.wikipedia.org/wiki/Hexapawn
    """

    def __init__(self, players, size=(4, 4)):
        self.size = M, N = size
        p = [[(i, j) for j in range(N)] for i in [0, M - 1]]

        for i, d, goal, pawns in [(0, 1, M - 1, p[0]), (1, -1, 0, p[1])]:
            players[i].direction = d
            players[i].goal_line = goal
            players[i].pawns = pawns
            players[i].starting_positions = copy.deepcopy(pawns)
            players[i].captured_pawns = []

        self.players = players
        self.current_player = 1

    def possible_moves(self):
        moves = []
        opponent_pawns = self.opponent.pawns
        d = self.player.direction
        for i, j in self.player.pawns:
            if (i + d, j) not in opponent_pawns:
                moves.append(((i, j), (i + d, j)))
            if (i + d, j + 1) in opponent_pawns:
                moves.append(((i, j), (i + d, j + 1)))
            if (i + d, j - 1) in opponent_pawns:
                moves.append(((i, j), (i + d, j - 1)))

        return list(map(to_string, [(i, j) for i, j in moves]))

    def make_move(self, move):
        move = list(map(to_tuple, move.split(" ")))
                
        pawn_index = self.player.pawns.index(move[0])
        self.player.pawns[pawn_index] = move[1]

        if move[1] in self.opponent.pawns:
            opponent_pawn_index = self.opponent.pawns.index(move[1])
            starting_position = self.opponent.starting_positions.pop(opponent_pawn_index)
            self.opponent.pawns.remove(move[1])
            self.opponent.captured_pawns.append(starting_position)

        if move[1][0] == self.opponent.goal_line:
            return
 
        if config.DETERMINISTIC:
            return

        if random.random() < config.PROBABILITY and self.opponent.captured_pawns:
            resurrected_pawn_index = random.choice(range(len(self.opponent.captured_pawns)))
            resurrected_pawn = self.opponent.captured_pawns.pop(resurrected_pawn_index) 
            self.opponent.pawns.append(resurrected_pawn)
            self.opponent.starting_positions.append(resurrected_pawn)

    def lose(self):
        return any([i == self.opponent.goal_line for i, j in self.opponent.pawns]) or (
            self.possible_moves() == []
        )

    def is_over(self):
        return self.lose()

    def show(self):
        f = (
            lambda x: "1"
            if x in self.players[0].pawns
            else ("2" if x in self.players[1].pawns else ".")
        )
        print(
            "\n".join(
                [
                    " ".join([f((i, j)) for j in range(self.size[1])])
                    for i in range(self.size[0])
                ]
            )
        )

if __name__ == "__main__":
    from easyAI import AI_Player, Human_Player 
    from AI import Negamax 

    scoring = lambda game: -100 if game.lose() else 0
    ai_depths = [2, 5, 15, 20]
    variants = ['Deterministic', 'Probabilistic']
    prunnings = [True, False]
    results = []

    for i in range(config.NUMBER_OF_GAMES):
        for depth in ai_depths:
            for variant in variants:
                for prunning in [True, False]: 
                    print('\n\n ========= Starting game %d at depth %d (%s %s) ========= \n' % (i, depth, variant, prunning))
                    config.DETERMINISTIC = (variant == 'Deterministic')
                    ai = Negamax(depth, scoring, prunning=prunning)
                    game = Hexapawn([AI_Player(ai), AI_Player(ai)])

                    start_time = time.time()
                    game.play()
                    elapsed_time = time.time() - start_time

                    winner = game.opponent_index
                    results.append([i, depth, variant, prunning, winner, elapsed_time])

    df = pd.DataFrame(results, columns=['Game', 'Depth', 'Variant', 'Prunning' ,'Winner', 'Time'])
    print(df)

    print('\n\nNumber of wins for each player at each depth and variant:')
    print(df.groupby(['Depth', 'Prunning', 'Variant', 'Winner']).size())

    average_times = df.groupby(['Variant', 'Prunning'])['Time'].mean()
    print('\n\nAverage times spent by each AI variant:')
    print(average_times)