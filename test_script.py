__author__ = 'josiah'
from MineSolver import MineSolver

mine = MineSolver()
blank_block = mine.servant.get_random_blank_block()
mine.reveal_squares([blank_block])
mine.solver()
