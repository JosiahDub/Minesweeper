__author__ = 'josiah'
from random import sample
from Tkinter import *
import json


class Minesweeper:
    def __init__(self, rows, columns, mines, gui=True):
        if mines > rows * columns:
            raise MineError('The number of mines exceeds the field size.')
        self.rows = rows
        self.columns = columns
        self.mines = mines
        self.gui = gui

        indices = [(row, column) for row in range(0, rows)
                   for column in range(0, columns)]
        self.mine_coordinates = sample(indices, self.mines)

        self.neighbors = [[0 for row in range(0, self.columns)]
                          for column in range(0, self.rows)]

        # Creates neighbor values
        # Loops through all mine_coordinates
        for mine in self.mine_coordinates:
            # Gets a 3x3 box around the mine. Technically includes mine
            coords = self.get_surrounding_block_coords(mine)
            for coord in coords:
                self.neighbors[coord[0]][coord[1]] += 1

        # List of all blocks with no mines neighboring
        self.zero_neighbors = self.get_zero_neighbors()

        # Exposed coordinates of the field as tuples
        self.exposed_field = []

        # Blocks newly exposed after a move as tuples
        self.newly_exposed = []

        # What the player sees
        self.field = [[-1 for row in range(0, self.columns)]
                      for column in range(0, self.rows)]

        # Coordinates of planted flags as tuples
        self.flags = []

        # GUI
        self.master = Tk()
        self.master.title('Minesweeper!')
        self.gui_colors = {'flag': 'green', 'bomb': 'red',
                           'unrevealed': 'light gray', 'revealed': 'dark gray'}

        # set up buttons
        # Dictionary: [button location tuple] = button handle
        # Has to be a tuple for a dictionary
        self.button_fields = {}
        for row in range(0, self.rows):
            for column in range(0, self.columns):
                button_handle = Button(self.master, width=1,
                                       background=self.gui_colors['unrevealed'])
                # Left click handler (reveal square)
                button_handle.bind('<ButtonRelease-1>',
                                   lambda event, button_tuple=(row, column):
                                   self.button_reveal(event, button_tuple))
                # Middle click handler (reveal multiple squares)
                button_handle.bind('<ButtonRelease-2>',
                                   lambda event, button_tuple=(row, column):
                                   self.button_mass_reveal(event, button_tuple))
                # Right click handler (plant flag)
                button_handle.bind('<ButtonRelease-3>',
                                   lambda event, button_tuple=(row, column):
                                   self.button_flag(event, button_tuple))
                button_handle.grid(row=(row + 1), column=column)
                self.button_fields[(row, column)] = button_handle

        if self.gui:
            self.master.mainloop()

    @classmethod
    def difficulty(cls, difficulty):
        """
        Creates a class based on the desired difficulty.
        :param difficulty:
        :return:
        """
        if difficulty == 'easy':
            rows = 8
            columns = 8
            mines = 10
        elif difficulty == 'medium':
            rows = 16
            columns = 16
            mines = 40
        elif difficulty == 'hard':
            rows = 16
            columns = 30
            mines = 99
        else:
            rows = 16
            columns = 16
            mines = 40
            print "Difficulty not recognized. Creating a medium game instead."
        mine = cls(rows, columns, mines)
        return mine

    def save_field_state(self, save_name, initial=False):
        """
        Saves the current configuration as a JSON file.
        :return:
        """
        minefield = {'rows': self.rows, 'columns': self.columns, 'mines': self.mines,
                     'neighbors': self.neighbors, 'mine_coords': self.mine_coordinates,
                     'flags': self.flags, 'exposed': self.exposed_field}
        if initial:
            minefield['flags'] = []
            minefield['exposed'] = []
        file_name = save_name + '.json'
        with open(file_name, 'w') as out_file:
            json.dump(minefield, out_file, separators=(',', ':'))

    @classmethod
    def load_state(cls, state, gui=False):
        """
        Creates a Minesweeper instance from a JSON file
        :param state:
        :param gui:
        :return:
        """
        with open(state, 'r') as state_file:
            state_dict = json.load(state_file)
        mine = cls(state_dict['rows'], state_dict['columns'], state_dict['mines'], gui=False)
        # Overrides required info
        # Since JSON doesn't know what a tuple is, we have to convert everything to one.
        mine.exposed_field = state_dict['exposed']
        for exposed_index in range(len(mine.exposed_field)):
            mine.exposed_field[exposed_index] = tuple(mine.exposed_field[exposed_index])
        mine.flags = state_dict['flags']
        for flag_index in range(len(mine.flags)):
            mine.flags[flag_index] = tuple(mine.flags[flag_index])
        mine.neighbors = state_dict['neighbors']
        for neighbor_index in range(len(mine.neighbors)):
            mine.neighbors[neighbor_index] = tuple(mine.neighbors[neighbor_index])
        mine.mine_coordinates = state_dict['mine_coords']
        for mine_index in range(len(mine.mine_coordinates)):
            mine.mine_coordinates[mine_index] = tuple(mine.mine_coordinates[mine_index])
        # Reforms zero_neighbors since that's not saved
        mine.zero_neighbors = mine.get_zero_neighbors()
        # Set up the buttons
        # Exposed
        for coord in mine.exposed_field:
            button_handle = mine.button_fields[coord]
            button_text = str(mine.neighbors[coord[0]][coord[1]])
            button_handle.configure(text=button_text)
        # Flags
        for coord in mine.flags:
            button_handle = mine.button_fields[coord]
            button_handle.configure(text='f')
            button_handle.configure(background=mine.gui_colors['flag'])
        # Runs the GUI if desired
        if gui:
            mine.master.mainloop()
        return mine

    def reset(self):
        """
        Returns the game to the beginning conditions.
        :return:
        """
        # Loops through all exposed and flagged blocks
        for coord in self.exposed_field + self.flags:
            button_handle = self.button_fields[coord]
            button_handle.configure(text='f')
            button_handle.configure(background=self.gui_colors['unrevealed'])
        # Resets coordinate lists
        self.flags = []
        self.exposed_field = []
        self.newly_exposed = []
        self.field = [[-1 for row in range(0, self.columns)]
                      for column in range(0, self.rows)]
        return self.field

    def get_zero_neighbors(self):
        """
        Returns all blocks with zero mines neighboring it.
        :return:
        """
        zero_neighbors = []
        for row_index in range(0, self.rows):
            for col_index in range(0, self.columns):
                if self.neighbors[row_index][col_index] == 0:
                    zero_neighbors.append((row_index, col_index))
        return zero_neighbors

    def button_reveal(self, event, button_tuple):
        """
        On left clicking a block, reveal it. Won't reveal a flagged block.
        :param event:
        :param button_tuple:
        :return:
        """
        # Delete required but useless event handle
        del event
        lose = False
        exposed_field = []
        newly_exposed = []
        if button_tuple not in self.flags:
            button_handle = self.button_fields[button_tuple]
            button_text = str(self.neighbors[button_tuple[0]][button_tuple[1]])
            button_handle.configure(text=button_text)
            lose, exposed_field, \
                newly_exposed = self.reveal_wrapper([button_tuple])
        return lose, exposed_field, newly_exposed

    def button_mass_reveal(self, event, button_tuple):
        """
        On middle click, reveal all squares if flags = neighbors.
        :param event:
        :param button_tuple:
        :return:
        """
        # Delete required but useless event handle
        del event
        lose = False
        exposed_field = []
        button_value = self.neighbors[button_tuple[0]][button_tuple[1]]
        # Button needs to be exposed and not flagged
        if button_tuple in self.exposed_field and button_tuple not in self.flags:
            # Neighbor must equal number of flags.
            if button_value == self.get_num_flag_neighbors(button_tuple):
                coords = self.get_surrounding_block_coords(button_tuple)
                lose, exposed_field, newly_exposed = self.reveal_wrapper(coords)
        return lose, exposed_field

    def button_flag(self, event, button_tuple):
        """
        On right click, add flag to block.
        :param event:
        :param button_tuple:
        :return:
        """
        # Delete required but useless event handle
        del event
        button_handle = self.button_fields[button_tuple]
        if button_tuple in self.flags:
            self.flags.remove(button_tuple)
            button_handle.configure(text='')
            button_handle.configure(background=self.gui_colors['unrevealed'])
        else:
            self.flags.append(button_tuple)
            button_handle.configure(text='f')
            button_handle.configure(background=self.gui_colors['flag'])
        return self.for_the_win(), self.get_exposed_field()

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

    # TODO: Candidate for deletion
    def get_flag_neighbor_coords(self, coordinate):
        """
        Returns the coordinates for all flags surrounding the coordinate.
        :param coordinate:
        :return:
        """
        flag_coords = []
        surrounding_coords = self.get_surrounding_block_coords(coordinate)
        for coord in surrounding_coords:
            if coord in self.flags:
                flag_coords.append(coord)
        return flag_coords

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

    def lose_game(self):
        print "You lose, and suck."
        return self.get_full_field()

    def win_game(self):
        print "You win. Good job. It was so tough."
        return self.get_full_field()

    def get_exposed_field(self):
        """
        Returns a MxN field exposed by the player.
        -1: Unexposed block
        0-8: number of neighboring mines
        'f': flag
        'b': bomb

        :return:
        """
        for index in self.exposed_field:
            self.field[index[0]][index[1]] = self.neighbors[index[0]][index[1]]
        for flag in self.flags:
            self.field[flag[0]][flag[1]] = 'f'
        return self.field

    def get_full_field(self):
        """
        Returns the entire field, minus flags.
        0-8: number of neighboring mines
        'b': bomb

        :return:
        """
        full_field = self.neighbors
        for mine in self.mine_coordinates:
            full_field[mine[0]][mine[1]] = 'b'
        return full_field

    def plant_flags(self, flag_coordinates):
        """
        Plants a flag on the desired blocks given as a list of 2x1 lists.

        Example: [[2, 1], [13, 17]]

        :param flag_coordinates:
        :return: Win status, exposed field
        """
        for coordinate in flag_coordinates:
            if coordinate not in self.flags:
                self.flags.append(coordinate)
            else:
                self.flags.remove(coordinate)
        # After planting (or removing), check for win
        return self.for_the_win(), self.get_exposed_field()

    def for_the_win(self):
        """
        Checks if won by comparing mines to flags.
        :return: Win status
        """
        win = False
        # First check if the number of flags matches the number of mines
        if len(self.flags) == self.mines:
            win = True
            for mine in self.mine_coordinates:
                if mine not in self.flags:
                    win = False
        return win

    def reveal_wrapper(self, coordinates):
        """
        Wraps reveal_squares, which is often called recursively.
        :param coordinates:
        :return: Lose status, exposed field, newly exposed indices
        """
        self.newly_exposed = []
        lose = self.reveal_squares(coordinates)
        return lose, self.get_exposed_field(), self.newly_exposed

    def reveal_squares(self, coordinates):
        """
        Reveals the desired blocks based on the desired list of 1x2 lists.

        If a block neighbor is 0, reveals all blocks around it.

        Adds newly revealed blocks with a neighbor value > 0 to list

        Example: [[2, 1], [13, 17]]

        :param coordinates:
        :return: Lose status
        """
        lose = False
        for coordinate in coordinates:
            # if this square has been flagged or already exposed, skip
            if coordinate not in self.flags and coordinate not in self.exposed_field:
                # You lose
                if coordinate in self.mine_coordinates:
                    button_text = 'b'
                    lose = True
                else:
                    button_text = self.neighbors[coordinate[0]][coordinate[1]]
                    self.exposed_field.append(coordinate)
                    # If the neighbor is empty, reveal its neighborhood
                    if button_text == 0:
                        coords = self.get_surrounding_block_coords(coordinate)
                        self.reveal_squares(coords)
                    # If the new block isn't zero, add it to the new list
                    else:
                        self.newly_exposed.append(coordinate)
                # Update the button if gui is on
                # self.gui should be here. this is for debug
                if True:
                    index_tuple = tuple(coordinate)
                    button_handle = self.button_fields[index_tuple]
                    button_handle.configure(text=button_text)
                    button_handle.configure(background=self.gui_colors['revealed'])
                    if button_text == 'b':
                        button_handle.configure(background=self.gui_colors['bomb'])
        return lose


class MineError(Exception):
    def __init__(self, mines):
        self.mines = mines

    def __str__(self):
        return repr(self.mines)
