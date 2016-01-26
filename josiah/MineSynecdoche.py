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
        self.rows = rows
        self.columns = columns
        self.neighbors = [[None for column in range(0, self.columns)]
                          for row in range(0, self.rows)]
        for coordinate in self.number_dictionary.keys():
            self.neighbors[coordinate[0]][coordinate[1]] = self.number_dictionary[coordinate]
        self.exposed_field = self.number_dictionary.keys()
        self.flags = []
        self.mine_coordinates = []
        # self.field = [[None for column in range(0, self.columns)]
        #               for row in range(0, self.rows)]

    def get_exposed_field(self):
        field = [[None for column in range(0, self.columns)]
                 for row in range(0, self.rows)]
        for coordinate in self.unrevealed:
            field[coordinate[0]][coordinate[1]] = -1
        for index in self.exposed_field:
            field[index[0]][index[1]] = self.number_dictionary[index]
        for flag in self.flags:
            field[flag[0]][flag[1]] = 'f'
        return field

    def plant_flag(self, coordinate):
        self.flags.append(coordinate)
        self.unrevealed.remove(coordinate)
        return self.get_exposed_field()
