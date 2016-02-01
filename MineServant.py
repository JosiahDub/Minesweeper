__author__ = 'josiah'
from random import choice


class MineServant:
    """
    This class contains several methods to get data useful to solving Minesweeper.
    """
    def __init__(self, mine):
        self.mine = mine
        self.color_coding = {'flag': 'green', 'bomb': 'red', 'unrevealed': 'yellow',
                             'zero': 'grey', 'number': 'white'}

    def reset(self):
        """
        Calls the Minesweeper reset function.
        :return:
        """
        self.mine.reset()

    def get_unrevealed_blocks(self, coordinate):
        """
        Returns the coordinates for all unrevealed blocks around a coordinate.
        :param coordinate:
        :return:
        """
        surrounding_coords = self.mine.get_surrounding_block_coords(coordinate)
        unrevealed_coords = []
        for coord in surrounding_coords:
            # If the coordinate isn't in exposed field or flags, it's unrevealed.
            if coord not in self.mine.exposed_field and coord not in self.mine.flags:
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
        # Gets the mines shared in surrounding coords and exposed field
        neighbor_coords = set(surrounding_coords).intersection(self.mine.exposed_field)
        # Remove original coordinate
        neighbor_coords.remove(coordinate)
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

    def custom_pretty_print_field(self, numbers, unrevealed=None, flags=None):
        """
        Prints a custom field based on desired blocks.
        :param numbers:
        :param unrevealed:
        :param flags:
        :return:
        """
        try:
            # noinspection PyUnresolvedReferences
            from termcolor import colored
        except ImportError:
            print "Install the termcolor module to use this method."
            return
        print_field = []
        for row in range(0, self.mine.rows):
            new_row = colored('', 'white')
            for column in range(0, self.mine.columns):
                # Unrevealed
                if unrevealed is not None and (row, column) in unrevealed:
                    # Gets the real block value for more accuracy.
                    new_row += colored('-1', self.color_coding['unrevealed'])
                # Numbered
                elif (row, column) in numbers:
                    block_value = self.get_real_block_value((row, column))
                    new_row += colored(' ' + str(block_value), self.color_coding['number'])
                elif flags is not None and (row, column) in flags:
                    new_row += colored(' f', self.color_coding['flag'])
                # Nothing. Two spaces
                else:
                    new_row += colored('  ', 'white')
            print_field.append(new_row)
        for row in print_field:
            print row

    def pretty_print_field(self):
        """
        Prints the field using color coding so you don't have to open the GUI.
        :return:
        """
        try:
            # noinspection PyUnresolvedReferences
            from termcolor import colored
        except ImportError:
            print "Install the termcolor module to use this method."
            return
        print_field = []
        for row in range(0, self.mine.rows):
            new_row = colored('', 'white')
            for column in range(0, self.mine.columns):
                # Unrevealed
                if (row, column) in self.mine.exposed_field:
                    # Bomb
                    if (row, column) in self.mine.mine_coordinates:
                        new_row += colored(' b', self.color_coding['bomb'])
                    else:
                        # Gets the real block value for more accuracy.
                        block_value = self.mine.neighbors[row][column]
                        # Zero
                        if block_value == 0:
                            new_row += colored(' 0', self.color_coding['zero'])
                        # 1-8
                        else:
                            new_row += colored(' ' + str(block_value), self.color_coding['number'])
                elif (row, column) in self.mine.flags:
                    new_row += colored(' f', self.color_coding['flag'])
                # Unexposed
                else:
                    new_row += colored('-1', self.color_coding['unrevealed'])
            print_field.append(new_row)
        for row in print_field:
            print row
