import numpy as np


class Board:
    """
    A class to represent a Connect Four board.

    Attributes:
        rows (int): The number of rows in the board.
        cols (int): The number of columns in the board.
        values (list): The possible values that can be placed on the board.
        board (np.ndarray): The game board represented as a 2D NumPy array.

    Methods:
        get_board(): Get the board
        set_board(row, col, value): Set the board
        print_board(): Prints the current state of the board.
        final_move(move): Checks if the given move results in a winning streak.
        valid_move(col): Checks if a move in the specified column is valid.
        valid_moves(): Returns a list of valid columns where a move can be made.
        get_next_open_row(col): Finds the next open row in the specified column.
    """

    def __init__(self, rows: int = 6, cols: int = 5):
        """Initialize a new Connect Four board.

        Args:
            rows (int, optional): The number of rows in the board. Defaults to 5.
            cols (int, optional): The number of columns in the board. Defaults to 6.
        """
        self.rows = rows
        self.cols = cols
        self.values = [0, 1, 2]
        self.shapes = [rows, cols]
        self.board = np.full((rows, cols), 2, dtype=int)

    def set_whole_board(self, board):
        """
        Set the entire board with a given 2D NumPy array.

        This method updates the current board with the provided 2D NumPy array.
        It also updates the number of rows and columns based on the shape of the array.

        Parameters:
        board (np.ndarray): A 2D NumPy array representing the new board state.
            The array should have shape (rows, cols), where rows and cols are the number of rows and columns in the board.

        Returns:
        None
        """
        self.board = board
        self.rows = board.shape[0]
        self.cols = board.shape[1]
        self.shapes = [board.shape[0], board.shape[1]]

    def get_board(self):
        """Get the board.

        Returns:
            np.ndarray: The game board represented as a 2D NumPy array.
        """
        return self.board

    def set_board(self, row: int, col: int, value: int):
        """
        Set the board at the specified row and column with the given value.

        Args:
            row (int): The row index where the value should be set.
            col (int): The column index where the value should be set.
            value (int): The value to be set at the specified position.

        Raises:
            ValueError: If the provided row, column, or value is invalid.
                - The row or column index is out of bounds.
                - The provided value is not in the list of valid values.

        Returns:
            None
        """
        if self.rows < row or self.cols < col or value not in self.values:
            raise ValueError
        self.board[row, col] = value

    def print_board(self):
        """Print the current state of the Connect Four board.
        The board is flipped upside down before printing.
        """
        print(np.flip(self.board, 0))

    def final_move(self, move: int) -> bool or int:
        """Checks if the given move forms a winning streak (four consecutive moves)
        on the provided board, considering horizontal, vertical, and diagonal directions.

        Args:
            move (int): The player's move (integer value).

        Returns:
            bool: True if a winning streak is found, False otherwise.
            int: 3 if the entire first row is filled (special case).
        """
        # Check horizontal streaks
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if np.all(self.board[r, c : c + 4] == move):
                    return True

        # Check vertical streaks
        for r in range(self.rows - 3):
            for c in range(self.cols):
                if np.all(self.board[r : r + 4, c] == move):
                    return True

        # Check diagonal streaks (bottom-left to top-right)
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if all(self.board[r + i, c + i] == move for i in range(4)):
                    return True

        # Check diagonal streaks (top-left to bottom-right)
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                if all(self.board[r - i, c + i] == move for i in range(4)):
                    return True

        # Check if the board is full (special case)
        if np.all(self.board[0] != 0):
            return 3

        return False

    def valid_move(self, col: int) -> bool:
        """Check if a move is valid by checking if the top row of the specified column is empty.

        Args:
            col (int): The column to check.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        return self.board[0, col] == 0

    def valid_moves(self) -> list:
        """Get a list of valid moves by checking which columns have an empty top row.

        Returns:
            list: A list of valid column indices.
        """
        return [c for c in range(self.cols) if self.board[0, c] == 0]

    def get_next_open_row(self, col: int) -> int:
        """Find the next open row in the specified column.

        Args:
            col (int): The column to check.

        Returns:
            int: The index of the next open row, or -1 if the column is full.
        """
        for r in range(self.rows - 1, -1, -1):
            if self.board[r, col] == 0:
                return r
        return -1

    def check_win(self):
        """
        Check if there is a winner in the game.

        Returns:
            int: The player number of the winner (1 for player 1, 0 for player 2, 2 for no winner).
        """

        def check_direction(row, col, dr, dc):
            """
            Check if there are four consecutive cells in the given direction.

            Parameters:
                row (int): The row index of the starting cell.
                col (int): The column index of the starting cell.
                dr (int): The row increment for the direction.
                dc (int): The column increment for the direction.

            Returns:
                int: The player number of the player who has four consecutive cells in
                     the given direction
                     (1 for player 1, 0 for player 2, None for no winner).
            """
            player = self.board[row, col]
            if player == 2:
                return None
            for i in range(1, 4):
                if self.board[row + i * dr, col + i * dc] != player:
                    return None
            return player

        for r in range(self.rows):
            for c in range(self.cols):
                if c <= self.cols - 4:
                    result = check_direction(r, c, 0, 1)  # Horizontal
                    if result is not None:
                        return result
                if r <= self.rows - 4:
                    result = check_direction(r, c, 1, 0)  # Vertical
                    if result is not None:
                        return result
                if c <= self.cols - 4 and r <= self.rows - 4:
                    result = check_direction(r, c, 1, 1)  # Diagonal down-right
                    if result is not None:
                        return result
                if c <= self.cols - 4 and r >= 3:
                    result = check_direction(r, c, -1, 1)  # Diagonal up-right
                    if result is not None:
                        return result

        return 2
