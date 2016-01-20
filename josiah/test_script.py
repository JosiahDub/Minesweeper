__author__ = 'josiah'
from josiah.MineSolver import MineSolver

# (6, 1) will not reveal final unrevealed

mine = MineSolver()
blank_block = mine.servant.get_random_blank_block()
mine.reveal_squares([blank_block])
mine.solver()
