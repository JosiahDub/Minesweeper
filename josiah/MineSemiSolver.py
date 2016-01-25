__author__ = 'josiah'
from MineSynecdoche import MineSynecdoche
from MineServant import MineServant
from itertools import combinations
from random import choice


class MineSemiSolver:
    def __init__(self, unrevealed, number_dictionary, rows, columns):
        self.unrevealed = unrevealed
        self.number_dictionary = number_dictionary
        self.rows = rows
        self.columns = columns
        self.flags_planted = 0
        self.mine = MineSynecdoche(unrevealed, number_dictionary, rows, columns)
        self.full_field = self.mine.get_exposed_field()
        self.servant = MineServant(self.mine)
        self.unchecked_blocks = self.number_dictionary.keys()
        self.blocks_to_remove = set([])
        self.possible_plays = []

    def reveal_squares(self, coordinate):
        # self.unrevealed.remove(coordinate)
        self.mine.unrevealed.remove(coordinate)

    def remove_checked_blocks(self):
        """
        Removes self.blocks_to_remove from self.unchecked_blocks.
        :return:
        """
        for block in self.blocks_to_remove:
            self.unchecked_blocks.remove(block)
        self.blocks_to_remove.clear()

    def choose(self):
        # TODO: self.servant full field is not getting updated, returning removed unrevealed.
        for coordinate in self.unchecked_blocks:
            print '*****COORDINATE*****', coordinate
            print 'global unrevealed: ', self.mine.unrevealed
            unrevealed = self.servant.get_unrevealed_blocks(coordinate)
            print 'unrevealed: ', unrevealed
            real_block_value = self.servant.get_real_block_value(coordinate)
            print 'block val: ', real_block_value
            # All possible locations of the mine(s). We need to only choose one.
            all_sets = combinations(unrevealed, real_block_value)
            chosen_placement = choice(list(all_sets))
            print 'chosen: ', chosen_placement
            not_chosen = set(unrevealed).copy()
            print 'not before: ', not_chosen
            for chosen in chosen_placement:
                not_chosen.remove(chosen)
                self.mine.flags.append(chosen)
                self.mine.unrevealed.remove(chosen)
            print 'not now: ', not_chosen
            for index in not_chosen:
                self.mine.unrevealed.remove(index)
        print self.unrevealed

    def flag_reveal_loop(self):
        """
        A loop to call flag_reveal_process in an efficient manner.
        :return:
        """
        solver_repeat = False
        flag_reveal_repeat = True
        # Do the easy stuff first
        while flag_reveal_repeat:
            # Will break out if no flag or reveal
            flag_reveal_repeat = False
            for coordinate in self.unchecked_blocks:
                # Check if there are any unrevealed blocks
                unrevealed = self.servant.get_unrevealed_blocks(coordinate)
                if unrevealed:
                    reveal, flag = self.flag_reveal_process(coordinate, unrevealed)
                    # If it hits even once, repeat flag/reveal
                    if reveal or flag:
                        flag_reveal_repeat = True
                # If not, schedule block for deletion after for loop.
                else:
                    self.blocks_to_remove.add(coordinate)
            # Remove blocks before moving on
            if self.blocks_to_remove:
                self.remove_checked_blocks()
        return solver_repeat

    def flag_reveal_process(self, coordinate, unrevealed):
        """
        Main process in which unrevealed blocks are found to reveal or flag.
        :param coordinate:
        :return:
        """
        reveal = False
        flag = False
        num_unrevealed = len(unrevealed)
        real_block_value = self.servant.get_real_block_value(coordinate)
        # All mines accounted for. Reveal rest
        if real_block_value == 0:
            self.reveal_squares(unrevealed)
            self.blocks_to_remove.add(coordinate)
            reveal = True
        # All unrevealed are mines. Flag them
        elif real_block_value == num_unrevealed:
            for coord in unrevealed:
                self.mine.flags.append(coord)
                self.flags_planted += 1
            self.blocks_to_remove.add(coordinate)
            flag = True
        return reveal, flag
