__author__ = 'josiah'
from itertools import combinations
from random import choice


class MineSemiSolver:
    def __init__(self, unrevealed, number_dictionary, rows, columns):
        self.number_dictionary = number_dictionary
        self.rows = rows
        self.columns = columns
        self.flags = []
        self.field = [[0 for column in range(0, self.columns)]
                      for row in range(0, self.rows)]
        for coordinate in self.number_dictionary.keys():
            self.field[coordinate[0]][coordinate[1]] = self.number_dictionary[coordinate]
        for coordinate in unrevealed:
            self.field[coordinate[0]][coordinate[1]] = -1
        self.unchecked_blocks = self.number_dictionary.keys()
        self.blocks_to_remove = set([])
        self.possible_plays = []

    def reveal_squares(self, coordinate):
        # self.unrevealed.remove(coordinate)
        self.field[coordinate[0]][coordinate[1]] = 0

    def plant_flag(self, coordinate):
        self.flags.append(coordinate)
        self.field[coordinate[0]][coordinate[1]] = 0

    def remove_checked_blocks(self):
        """
        Removes self.blocks_to_remove from self.unchecked_blocks.
        :return:
        """
        for block in self.blocks_to_remove:
            self.unchecked_blocks.remove(block)
        self.blocks_to_remove.clear()

    def choose(self):
        for coordinate in self.unchecked_blocks:
            real_block_value = self.get_real_block_value(coordinate)
            unrevealed = self.get_unrevealed_blocks(coordinate)
            if real_block_value <= 0 or len(unrevealed) == 0:
                continue
            # All possible locations of the mine(s). We need to only choose one.
            all_sets = combinations(unrevealed, real_block_value)
            chosen_placement = choice(list(all_sets))
            not_chosen = set(unrevealed).copy()
            for chosen in chosen_placement:
                self.plant_flag(chosen)
                not_chosen.remove(chosen)
            for index in not_chosen:
                self.field[index[0]][index[1]] = 0

    def get_real_block_value(self, coordinate):
        """
        Returns the real block value, subtracting neighboring flags.
        :param coordinate:
        :return:
        """
        block_value = self.field[coordinate[0]][coordinate[1]]
        flags = self.get_num_flag_neighbors(coordinate)
        return block_value - flags

    def get_unrevealed_blocks(self, coordinate):
        """
        Returns the coordinates for all unrevealed blocks around a coordinate.
        :param coordinate:
        :return:
        """
        surrounding_coords = self.get_surrounding_block_coords(coordinate)
        unrevealed_coords = []
        for coord in surrounding_coords:
            if self.field[coord[0]][coord[1]] == -1:
                unrevealed_coords.append(coord)
        return unrevealed_coords

    def get_num_flag_neighbors(self, coordinate):
        """
        Returns number of flags around the square
        :param coordinate:
        :return:
        """
        flag_neighbors = 0
        surrounding_coords = set(self.get_surrounding_block_coords(coordinate))
        for coord in surrounding_coords:
            if coord in self.flags:
                flag_neighbors += 1
        return flag_neighbors

    def get_surrounding_block_coords(self, coordinate):
        """
        Gets the coordinates for all blocks surrounding the desires coords.
        :param coordinate:
        :return:
        """
        # Rows
        # On bottom
        if coordinate[0] == self.rows - 1:
            start_row = coordinate[0] - 1
            end_row = self.rows - 1
        # On top
        elif coordinate[0] == 0:
            start_row = 0
            end_row = 1
        # Middle
        else:
            start_row = coordinate[0] - 1
            end_row = coordinate[0] + 1
        # Columns
        # On left edge
        if coordinate[1] == self.columns - 1:
            start_column = coordinate[1] - 1
            end_column = self.columns - 1
        # On right edge
        elif coordinate[1] == 0:
            start_column = 0
            end_column = 1
        # Middle
        else:
            start_column = coordinate[1] - 1
            end_column = coordinate[1] + 1
        # Create list of lists for the range
        surrounding_blocks = [(row, column)
                              for row in range(start_row, end_row + 1)
                              for column in range(start_column, end_column + 1)]
        return surrounding_blocks
