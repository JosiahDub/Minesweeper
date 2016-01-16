__author__ = 'josiah'
from random import choice
from math import fabs


class MineServant:
    """
    This class contains several methods to get data useful to solving Minesweeper.
    """
    def __init__(self, mine):
        self.mine = mine
        self.full_field = mine.get_exposed_field()
        self.color_coding = {'flag': 'green', 'bomb': 'red', 'unrevealed': 'yellow',
                             'zero': 'grey', 'number': 'white'}

    def get_unrevealed_blocks(self, coordinate):
        """
        Returns the coordinates for all unrevealed blocks around a coordinate.
        :param coordinate:
        :return:
        """
        surrounding_coords = self.mine.get_surrounding_block_coords(coordinate)
        unrevealed_coords = []
        for coord in surrounding_coords:
            if self.full_field[coord[0]][coord[1]] == -1:
                unrevealed_coords.append(coord)
        return unrevealed_coords

    def get_real_block_value(self, coordinate):
        """
        Returns the real block value, subtracting neighboring flags.
        :param coordinate:
        :return:
        """
        block_value = self.mine.neighbors[coordinate[0]][coordinate[1]]
        flags = self.mine.get_num_flag_neighbors(coordinate)
        return block_value - flags

    def get_neighbor_blocks(self, coordinate):
        """
        Returns coordinates for all neighbor blocks (value 1-8) surrounding the coordinate.
        :param coordinate:
        :return:
        """
        surrounding_coords = self.mine.get_surrounding_block_coords(coordinate)
        neighbor_coords = []
        for coord in surrounding_coords:
            # Do not return the original coordinate
            if coord != coordinate and 0 < self.full_field[coord[0]][coord[1]] < 9:
                neighbor_coords.append(coord)
        return neighbor_coords

    def get_exposed_neighbor_coords(self, coordinate):
        """
        Returns the coordinates of all exposed blocks surrounding the coordinate.
        :param coordinate:
        :return:
        """
        surrounding_coords = set(self.mine.get_surrounding_block_coords(coordinate))
        surrounding_coords.intersection_update(self.mine.exposed_field)
        return surrounding_coords

    def get_random_blank_block(self):
        """
        Returns a random blank block. Good for starting a game.
        :return:
        """
        return choice(self.mine.zero_neighbors)

    def get_fifty_fifty_mine(self, coordinate_set):
        """
        Returns the coordinate for a mine found in a set of two blocks with a 50/50 chance of having
        the mine.

        Returns None if neither block has a mine.

        :param coordinate_set:
        :return:
        """
        if coordinate_set[0] in self.mine.mine_coordinates:
            mine_coordinate = coordinate_set[0]
        elif coordinate_set[1] in self.mine.mine_coordinates:
            mine_coordinate = coordinate_set[1]
        else:
            mine_coordinate = None
        return mine_coordinate

    def get_all_unrevealed_blocks(self):
        """
        Returns all unrevealed blocks, based on the exposed blocks and flags.

        Might be good for nearing the end.
        :return:
        """
        indices = set([(row, column) for row in range(0, self.mine.rows)
                      for column in range(0, self.mine.columns)])
        return indices.difference(self.mine.exposed_field, self.mine.flags)

    def pretty_print_field(self):
        """
        Prints the field using color coding so you don't have to open the GUI.
        :return:
        """
        try:
            from termcolor import colored
        except ImportError:
            print "Install the termcolor module to use this method."
            return
        print_field = []
        for row in self.full_field:
            new_row = colored('', 'white')
            for block in row:
                # Unrevealed: yellow
                if block == -1:
                    new_row += colored('-1', self.color_coding['unrevealed'])
                # Revealed: zero
                elif block == 0:
                    new_row += colored(' ' + str(block), self.color_coding['zero'])
                # Revealed: greater than zero
                elif 1 <= block <= 8:
                    new_row += colored(' ' + str(block), self.color_coding['number'])
                # Flagged: green
                elif block == 'f':
                    new_row += colored(' ' + block, self.color_coding['flag'])
                # Bomb: red
                elif block == 'b':
                    new_row += colored(' ' + block, self.color_coding['bomb'])
            print_field.append(new_row)
        for row in print_field:
            print row
