To use:
mine = Minesweeper(rows, columns, mines, gui=False)
gui will launch the GUI upon initialization.

You can also create games based on difficulty:
mine = Minesweeper.difficulty('hard')

Or load a game from a saved game.
mine = Minesweeper.load_state('saved_game.json')

To save a game:
mine.save_state('saved_game.json')
To save the beginning configuration:
mine.save_state('saved_game.json', initial=True)

To reveal squares, any number you'd like:
lose, exposed_field, newly_exposed = mine.reveal_wrapper([(list of coordinate tuples)])
Example: mine.reveal_wrapper([(1, 2), (5, 16)])
newly_exposed contains all non-zero blocks exposed on the last move. This may be helpful to keep
track of what needs to be looked at.

To plant flags:
win, exposed_field = mine.plant_flags([(list of coordinate tuples)])
Example: win, exposed_field = mine.plant_flags([(1, 2), (5, 16)])

When submitting only one block, you must still enclose it with [].

You can use the GUI, but that is just to test the programming, not for real playing.

On the exposed field:
-1: unrevealed square
0-8: Number of neighboring mines
'f': flag, green background
'b': bomb, red background

To keep track of your progress using the GUI, use the Minesweeper.button_ functions. button_reveal
and button_flag are the most useful. The first argument is an event for the GUI. Pass in None.

Note: If you quit the GUI, Tkinter deletes the handles to the buttons, so you can use the button_
functions any more. Sorry.

To win: plant a flag on every mine, with no extras
To lose: step on a mine. Idiot.
Note: the game doesn't stop on losing/winning. They're for your benefit only.

Standard rules of minesweeper apply:
Flagged squares cannot be revealed.
When exposing a square with 0 bombs neighboring it, all surrounding squares are
    automatically revealed.

Yes you can cheat:
mines.mine_indices
But then you'd suck. It's kind of hard to hide data in python.

MineServant contains several functions that will probably be helpful for you.
Here are some must-use functions:
(row, column) = MineServant.get_random_blank_block()
Returns a random block with value 0. This is a good starting point for every game. It's not
guaranteed you'll get a good reveal.

((x1, y1), (x2, y2)) = MineServant.get_fifty_fifty_mine([(two coordinate tuples)])
If you've whittled down the field to two adjacent blocks with a 50/50 chance of having a mine, this
function just gives you the mine. You worked hard. You earned that mine!
