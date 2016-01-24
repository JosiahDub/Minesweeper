__author__ = 'josiah'


class MineSynecdoche:
    """
    Fake Minesweeper class used to fake solve a section of the real thing.

    Synecdoche, according to dictionary.com:
    a figure of speech in which a part is used for the whole or the whole for a part.
    """
    def __init__(self, unrevealed, number_dictionary, rows, columns):
        self.unrevealed = unrevealed
        self.number_dictionary = number_dictionary
        self.neighbors = self.number_dictionary.keys()
        self.exposed_field = self.neighbors.copy()
        self.rows = rows
        self.columns = columns
        self.flags = []
        self.mine_coordinates = []
        self.field = [[None for row in range(0, self.columns)]
                      for column in range(0, self.rows)]

    def get_exposed_field(self):
        for index in self.exposed_field:
            self.field[index[0]][index[1]] = self.neighbors[index[0]][index[1]]
        for flag in self.flags:
            self.field[flag[0]][flag[1]] = 'f'
        return self.field

    def get_num_flag_neighbors(self, coordinate):
        """
        Returns number of flags around the square
        :param coordinate:
        :return:
        """
        flag_neighbors = 0
        surrounding_coords = self.get_surrounding_block_coords(coordinate)
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
