__author__ = 'josiah'
from MineServant import MineServant
from itertools import combinations
from random import choice


class MineSemiSolver:
    def __init__(self, unrevealed, neighbors, rows, columns):
        self.unrevealed = unrevealed
        self.neighbors = neighbors
        self.rows = rows
        self.columns = columns
        self.flags = []
        self.servant = MineServant(self)
        self.exposed_field = self.neighbors.keys()
        self.possible_plays = []
        self.color_coding = {'flag': 'green', 'bomb': 'red', 'unrevealed': 'yellow',
                             'zero': 'grey', 'number': 'white'}

    def choose(self):
        self.servant.custom_pretty_print_field(self.exposed_field,
                                               unrevealed=self.unrevealed, flags=self.flags)
        for coordinate in self.exposed_field:
            print '*****COORDINATE*****', coordinate
            real_block_value = self.servant.get_real_block_value(coordinate)
            unrevealed = self.get_unrevealed_blocks(coordinate)
            if real_block_value == 0 and len(unrevealed) > 0:
                for index in unrevealed:
                    self.unrevealed.remove(index)
                continue
            if real_block_value < 0 or len(unrevealed) == 0:
                continue
            # All possible locations of the mine(s). We need to only choose one.
            all_sets = combinations(list(unrevealed), real_block_value)
            # Validates all moves
            valid_moves = []
            for move_set in all_sets:
                valid_move = self.negative_neighbor_move_validation(move_set)
                # TODO: Incorporate isolated_neighbor_move_validation
                # Adds valid moves to the list
                if valid_move:
                    valid_moves.append(move_set)
            try:
                chosen_placement = choice(valid_moves)
                print 'chosen move: ', chosen_placement
            except IndexError:
                print 'no moves!'
            else:
                # Remove blocks first
                for index in unrevealed:
                    self.unrevealed.remove(index)
                # Then flag and remove blocks around neighbors
                for chosen in chosen_placement:
                    self.flags.append(chosen)
                    self.remove_neighbor_unrevealed(chosen)
                self.servant.custom_pretty_print_field(self.exposed_field,
                                                       unrevealed=self.unrevealed,
                                                       flags=self.flags)
        self.servant.custom_pretty_print_field(self.exposed_field, unrevealed=self.unrevealed,
                                               flags=self.flags)

    def negative_neighbor_move_validation(self, coordinate_set):
        """
        Validates move by looking if neighbor values go negative
        :param coordinate_set:
        :return:
        """
        valid_move = True
        shared_neighbors = self.servant.get_neighbor_blocks(coordinate_set[0])
        # Get all neighbors that border the move set
        for coordinate in coordinate_set[1:]:
            new_neighbors = self.servant.get_neighbor_blocks(coordinate)
            shared_neighbors.intersection_update(new_neighbors)
        # Loop through and check if any are too low.
        for neighbor in shared_neighbors:
            block_value = self.servant.get_real_block_value(neighbor)
            # Any neighbor can invalidate the move
            if block_value < len(coordinate_set):
                valid_move = False
                break
        return valid_move

    # TODO: Take account of blocks to remove from surrounding neighbors and if those blocks isolate
    def isolated_neighbor_move_validation(self, coordinate, move_set, blocks_to_remove):
        """
        Validates moves by checking that another coordinate does not become isolated with no mines.
        :param coordinate:
        :param move_set:
        :param blocks_to_remove:
        :return:
        """
        # Have to look at it from the perspective of the blocks to remove
        print 'blocks to remove: ', blocks_to_remove
        print 'move set: ', move_set
        # Check doesn't need to be performed for zero blocks
        if len(blocks_to_remove) > 0:
            # Gets the neighbors attached to the blocks to remove
            neighbors = self.servant.get_neighbor_blocks(blocks_to_remove[0])
            for block in blocks_to_remove[1:]:
                neighbors.update(self.servant.get_neighbor_blocks(block))
                print 'growing neighbors: ', neighbors
            # Remove original coordinate
            neighbors.remove(coordinate)
            # Now look at each neighbor and their unrevealed
            for neighbor in neighbors:
                neighbor_block_value = self.servant.get_real_block_value(neighbor)
                # Skip the neighbor if neighbor has been dealt
                if neighbor_block_value == 0:
                    continue
                neighbor_unrevealed = self.get_unrevealed_blocks(neighbor)
                # Remove unrevealed from the move
                for block in blocks_to_remove:
                    if block in neighbor_unrevealed:
                        neighbor_unrevealed.remove(block)
                # If there are fewer blocks than the value, then the move is bad
                if len(neighbor_unrevealed) < neighbor_block_value:
                    valid_move = False
        return valid_move

    def remove_neighbor_unrevealed(self, flag_coordinate):
        """
        Removes all blocks around all neighbors with zero value.
        :param flag_coordinate:
        :return:
        """
        neighbors = self.servant.get_neighbor_blocks(flag_coordinate)
        # Loop through all neighbors
        for neighbor in neighbors:
            block_value = self.servant.get_real_block_value(neighbor)
            # Remove all blocks if zero
            if block_value == 0:
                blocks_to_reveal = self.get_unrevealed_blocks(neighbor)
                for block in blocks_to_reveal:
                    self.unrevealed.remove(block)

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

    # TODO: Can be inherited from Minesweeper
    def get_num_flag_neighbors(self, coordinate):
        """
        Returns number of flags around the coordinate
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

    # TODO: Can be inherited from Minesweeper
    def get_surrounding_block_coords(self, coordinate):
        """
        Gets the coordinates for all blocks surrounding the desires coords.
        :param coordinate:
        :return:
        """
        # Will choose 0 if coordinate is 0
        start_row = max(0, coordinate[0] - 1)
        # Will choose rows - 1 if coordinate is rows - 1
        end_row = min(coordinate[0] + 1, self.rows - 1)
        start_column = max(0, coordinate[1] - 1)
        end_column = min(coordinate[1] + 1, self.columns - 1)
        # Create list of lists for the range
        surrounding_blocks = [(row, column)
                              for row in range(start_row, end_row + 1)
                              for column in range(start_column, end_column + 1)]
        return set(surrounding_blocks)
