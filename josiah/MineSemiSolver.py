__author__ = 'josiah'
from itertools import combinations
from random import choice


class MineSemiSolver:
    def __init__(self, unrevealed, number_dictionary, rows, columns):
        self.unrevealed = unrevealed
        self.number_dictionary = number_dictionary
        self.rows = rows
        self.columns = columns
        self.flags = []
        self.field = [[0 for column in range(0, self.columns)]
                      for row in range(0, self.rows)]
        self.unchecked_blocks = self.number_dictionary.keys()
        self.blocks_to_remove = set([])
        self.possible_plays = []

    def plant_flag(self, coordinate):
        self.flags.append(coordinate)
        self.unrevealed.remove(coordinate)

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
            print '*****COORDINATE*****', coordinate
            real_block_value = self.get_real_block_value(coordinate)
            print 'real block value: ', real_block_value
            unrevealed = self.get_unrevealed_blocks(coordinate)
            print 'unrevealed: ', unrevealed
            if real_block_value <= 0 or len(unrevealed) == 0:
                continue
            # All possible locations of the mine(s). We need to only choose one.
            all_sets = combinations(list(unrevealed), real_block_value)
            chosen_placement = choice(list(all_sets))
            print 'chosen set: ', chosen_placement
            not_chosen = set(unrevealed).copy()
            for chosen in chosen_placement:
                self.plant_flag(chosen)
                not_chosen.remove(chosen)
            for index in not_chosen:
                self.unrevealed.remove(index)
            print 'global unrevealed: ', self.unrevealed

    def get_real_block_value(self, coordinate):
        """
        Returns the real block value, subtracting neighboring flags.
        :param coordinate:
        :return:
        """
        block_value = self.number_dictionary[coordinate]
        flags = self.get_num_flag_neighbors(coordinate)
        return block_value - flags

    def get_unrevealed_blocks(self, coordinate):
        """
        Returns the coordinates for all unrevealed blocks around a coordinate.
        :param coordinate:
        :return:
        """
        # Gets all surrounding coordinates
        unrevealed_coords = self.get_surrounding_block_coords(coordinate)
        # Reduces to what's in self.unrevealed
        unrevealed_coords.intersection_update(self.unrevealed)
        return unrevealed_coords

    def get_num_flag_neighbors(self, coordinate):
        """
        Returns number of flags around the square
        :param coordinate:
        :return:
        """
        # Gets all surrounding coordinates
        flag_coords = self.get_surrounding_block_coords(coordinate)
        # Reduces to what's in self.flags
        flag_coords.intersection_update(self.flags)
        # Gets the length of that
        flag_neighbors = len(flag_coords)
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
        return set(surrounding_blocks)
