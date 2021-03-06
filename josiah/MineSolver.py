__author__ = 'josiah'
from Minesweeper import Minesweeper
from MineServant import MineServant
from MineSemiSolver import MineSemiSolver


class MineSolver:
    """
    Solves Minesweeper by running through a few algorithms:
    Flag/reveal
    Confined Mine
    Shared Mine
    """

    def __init__(self, load_game=None):
        self.rows = 16
        self.columns = 30
        self.num_mines = 99
        if load_game is None:
            self.mine = Minesweeper(self.rows, self.columns, self.num_mines, gui=False)
        else:
            self.mine = Minesweeper.load_state(load_game)
        self.servant = MineServant(self.mine)
        self.exposed_indices = self.mine.exposed_field
        # Move these to self.exposed_field
        self.newly_exposed = []
        # Add block indices to here as they're revealed
        self.unchecked_blocks = []
        # Blocks scheduled to be removed after some processes for loops
        self.blocks_to_remove = set([])
        self.flags_planted = 0
        # Lose/win status. Both start as false naturally
        self.lose = False
        self.win = False
        self.semi_solver = None

    def reveal_squares(self, coordinate):
        """
        Calls the Minesweeper button_reveal function so progress can be tracked with the GUI.
        :param coordinate:
        :return:
        """
        for coord in coordinate:
            self.lose, self.newly_exposed = self.mine.button_reveal(None, coord)
            self.unchecked_blocks.extend(self.newly_exposed)

    def logical_solver(self):
        """
        Process that loops through unchecked blocks and runs the flag/reveal process.
        :return:
        """
        # Will break out if no moves found
        solver_repeat = True
        while solver_repeat:
            # Try the easy stuff
            solver_repeat = self.flag_reveal_loop()
            # Now try the hard stuff
            for coordinate in self.unchecked_blocks:
                unrevealed = self.servant.get_unrevealed_blocks(coordinate)
                if unrevealed:
                    area_reveal, area_flag = self.confined_mine_process(coordinate, unrevealed)
                    if self.lose:
                        print "Somehow we lost?! It's your fault."
                        return
                    # Break out of hard stuff and go to flag/reveal
                    if area_reveal or area_flag:
                        solver_repeat = True
                        break
                    # Check for a shared mine
                    shared_reveal, shared_flag = self.shared_mine_process(coordinate)
                    if self.lose:
                        print "Somehow we lost?! It's your fault."
                        return
                    if shared_reveal or shared_flag:
                        solver_repeat = True
                        break
                # Schedule block for deletion after for loop.
                else:
                    self.blocks_to_remove.add(coordinate)
            if self.blocks_to_remove:
                self.remove_checked_blocks()
        print "Out of moves. Full field:"
        # Quasi pretty-prints the field for the console.
        self.servant.pretty_print_field()
        if self.win:
            print "You won, because you're the best maybe."

    def probability_guesser(self):
        """

        :return:
        """
        # Get all unrevealed blocks that touch unchecked blocks
        blocks_to_guess = set([])
        numbers_dictionary = {}
        for coordinate in self.unchecked_blocks:
            numbers_dictionary[coordinate] = self.servant.get_real_block_value(coordinate)
            unrevealed_blocks = self.servant.get_unrevealed_blocks(coordinate)
            blocks_to_guess.update(unrevealed_blocks)
        # self.servant.custom_pretty_print_field(self.exposed_field, blocks_to_guess)
        self.semi_solver = MineSemiSolver(blocks_to_guess, numbers_dictionary, self.rows, self.columns)
        self.semi_solver.choose()
        # self.servant.custom_pretty_print_field(self.exposed_field, unrevealed=blocks_to_guess)

    def remove_checked_blocks(self):
        """
        Removes self.blocks_to_remove from self.exposed_field.
        :return:
        """
        for block in self.blocks_to_remove:
            self.unchecked_blocks.remove(block)
        self.blocks_to_remove.clear()

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
                    if self.lose:
                        print "Somehow we lost?! It's your fault."
                        return
                # If not, schedule block for deletion after for loop.
                else:
                    self.blocks_to_remove.add(coordinate)
            # Remove blocks before moving on
            if self.blocks_to_remove:
                self.remove_checked_blocks()
            if self.win:
                solver_repeat = False
                break
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
                self.win = self.mine.button_flag(None, coord)
                self.flags_planted += 1
            self.blocks_to_remove.add(coordinate)
            flag = True
        return reveal, flag

    def confined_mine_process(self, coordinate, unrevealed):
        """
        Check if a mine is enclosed in an area, and if surrounding blocks can be flagged or
        revealed.
        :param coordinate:
        :return:
        """
        reveal = False
        flag = False
        mines_in_area = self.servant.get_real_block_value(coordinate)
        # starts with first block, then whittles down
        similar_neighbors = set(self.servant.get_exposed_neighbor_coords(unrevealed[0]))
        for block in unrevealed[1:]:
            # gets the neighbors of the next block
            block_neighbors = self.servant.get_exposed_neighbor_coords(block)
            similar_neighbors.intersection_update(block_neighbors)
        # Now we have a list of shared neighbors. We need to check them all.
        for neighbor in similar_neighbors:
            real_block_value = self.servant.get_real_block_value(neighbor)
            # starts as full
            blocks_out_of_area = set(self.servant.get_unrevealed_blocks(neighbor))
            # Gets rid of blocks in unrevealed
            blocks_out_of_area.difference_update(unrevealed)
            num_outside = len(blocks_out_of_area)
            if num_outside > 0:
                # Flag blocks outside of area.
                if real_block_value == num_outside + mines_in_area:
                    for block in blocks_out_of_area:
                        self.win = self.mine.button_flag(None, block)
                        self.flags_planted += 1
                    flag = True
                # Reveal blocks outside area
                if real_block_value == mines_in_area:
                    self.reveal_squares(blocks_out_of_area)
                    reveal = True
        return reveal, flag

    def shared_mine_process(self, coordinate):
        """
        Loop through all neighbors and check if they share mines.
        :return:
        """
        flag = False
        reveal = False
        neighbor_blocks = self.servant.get_neighbor_blocks(coordinate)
        real_block_value = self.servant.get_real_block_value(coordinate)
        # Loops through all neighbors
        for neighbor in neighbor_blocks:
            # Don't do checked neighbors
            if neighbor not in self.unchecked_blocks:
                continue
            # Find shared unrevealed blocks
            blocks_unrevealed = set(self.servant.get_unrevealed_blocks(coordinate))
            neighbor_unrevealed = set(self.servant.get_unrevealed_blocks(neighbor))
            # Get all unrevealed blocks shared by the neighbors
            shared_unrevealed = blocks_unrevealed.intersection(neighbor_unrevealed)
            num_shared = len(shared_unrevealed)
            neighbor_real_block_value = self.servant.get_real_block_value(neighbor)
            possible_area_mines = min(real_block_value, neighbor_real_block_value, num_shared)
            neighbors_outside_area = len(neighbor_unrevealed) - num_shared
            if neighbors_outside_area > 0 and \
                    neighbor_real_block_value == neighbors_outside_area + possible_area_mines:
                # Flag neighbor blocks not shared with coordinate
                for block in neighbor_unrevealed.difference(blocks_unrevealed):
                    self.win = self.mine.button_flag(None, block)
                    self.flags_planted += 1
                flag = True
                # Check if the original block can reveal things.
                if real_block_value == possible_area_mines:
                    # Reveal blocks not shared with neighbor
                    self.reveal_squares(blocks_unrevealed.difference(neighbor_unrevealed))
                    reveal = True
        return reveal, flag
