__author__ = 'josiah'
from josiah.MineSolver import MineSolver

# (14, 1) will sometimes not flag final unrevealed

mine = MineSolver()
blank_block = mine.servant.get_random_blank_block()
mine.reveal_squares([blank_block])
mine.solver()
