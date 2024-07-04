import random
import math
import numpy as np

from Board import Board
import copy

CC = 2


class MCTSTreeNode:
    """
    A class used to represent a node in the Monte Carlo Tree Search (MCTS) algorithm.

    Attributes
    ----------
    state : Board
        the state of the board at this node
    score : int
        the score of the node, initially set to 0
    visits : int
        the number of times the node has been visited, initially set to 0
    parent : MCTSTreeNode
        the parent node of this node
    children : list
        the list of child nodes of this node
    turn : int
        the turn of the player at this node
    Poss_Child : List of Board
        the array of possible child nodes of this node
    level : int
        the level of the player at this node (0 for player 1, 1 for player 2)

    Methods
    -------
    __init__(self, state, parent, turn, level)
        Constructs all the necessary attributes for the MCTSTreeNode object.
    check_draw(self)
        Check if the game is a draw.
    get_neighbour_moves(self, level)
        Generate all possible successor states from the current state.
    selection(self)
        Select the best child node based on the UCB1 formula.
    expansion(self)
        Expands the game tree by selecting a random successor state.
    simulation(self, level)
        Simulates a game from the current board state.
    update(self, result)
        Update the scores and visits based on the simulation result.
    """

    def __init__(self, state, parent=None, turn: int = 0, level: int = 0):
        """
        Constructs all the necessary attributes for the MCTSTreeNode object.

        Parameters
        ----------
        state (Board):
            the state of the board at this node
        parent : MCTSTreeNode or None
            the parent node of this node
        turn : int
            the turn of the player at this node
        level : int
            the level of the player at this node (0 for player 1, 1 for player 2)
        """
        self.state = state
        self.score = 0
        self.visits = 0
        self.parent = parent
        self.children = []
        self.turn = turn
        self.Poss_Child = self.get_neighbour_moves(level)
        self.level = level
        self.is_terminal = self.check_is_terminal()

    def check_is_terminal(self) -> bool:
        """
        Check if the current state of the game is a terminal state.

        A terminal state is defined as a state where the game has ended, either in a win, loss, or draw condition.

        Parameters:
        self (MCTSTreeNode): The current node in the Monte Carlo Tree Search (MCTS) tree.

        Returns:
        bool: True if the game is in a terminal state, False otherwise.

        The function checks if the game is in a terminal state by calling the `check_win()`
        of the current node. If the result is 2 (indicating a draw), it further checks if the game is a draw by calling
        the `check_draw()` method. If either of these conditions is met, the function returns True;
        otherwise, it returns False.
        """
        return self.state.check_win() == 2 and not self.check_draw()

    def check_draw(self):
        """
        Check if the game is a draw.

        Returns:
        bool: True if the game is a draw, False otherwise.

        The function checks if the game is a draw by verifying that no player has won and
        that all columns in the top row of the board are filled.
        """
        if self.state.check_win() == 0 or self.state.check_win() == 1:
            return False
        else:
            result = 0
            board = self.state.get_board()
            for c in range(self.state.shapes[1]):
                result |= board[0, c]
            return not (result & 2)

    def get_neighbour_moves(self, level):
        """
        Generate all possible successor states from the given parent state.

        Parameters:
        level (int): The player number (0 for player 2, 1 for player 1).

        Returns:
        np.ndarray: An array of successor states (2D arrays) representing the possible moves
        from the given parent state.
        """
        child_nodes = []
        for i in range(self.state.shapes[1]):
            board_cpy = copy.deepcopy(self.state)
            if board_cpy.get_board()[0, i] == 2:
                for j in range(self.state.shapes[0]):
                    if board_cpy.get_board()[self.state.shapes[0] - j - 1, i] == 2:
                        board_cpy.set_board(self.state.shapes[0] - j - 1, i, level ^ 1)
                        child_nodes.append(board_cpy)
                        break
        return np.array(child_nodes)

    def selection(self):
        """
        Select the best child node from the parent node based on the UCB1 formula.

        Returns:
        MCTSTreeNode: The selected child node based on the UCB1 formula.
        """
        n = len(self.children)
        best_score = -100
        best_child = self
        for i in range(n):
            if self.children[i].visits == 0:
                return self.children[i]
            else:
                score = self.children[i].score / self.children[i].visits
                score += math.sqrt(CC * math.log(self.visits) / self.children[i].visits)
                if score > best_score:
                    best_score = score
                    best_child = self.children[i]
        return best_child

    def expansion(self):
        """
        Expands the game tree by selecting a random successor state from the parent node's possible child states.

        Returns:
        MCTSTreeNode: The newly created child node representing the selected successor state.

        Note:
        This function also updates the parent node's list of possible child states by removing
        the selected successor state.
        """
        next_node = random.choice(self.Poss_Child)
        self.Poss_Child = np.delete(
            self.Poss_Child, np.where(self.Poss_Child == next_node), axis=0
        )
        child = MCTSTreeNode(next_node, self, 1 ^ self.turn, self.level ^ 1)
        self.children.append(child)
        return child

    def simulation(self, level):
        """
        Simulates a game from the given board state and level.

        Parameters:
        level (int): The player number (0 for player 2, 1 for player 1).

        Returns:
        int: The result of the simulation (1 for player 1 win, 0 for player 2 win, 2 for draw).

        The function repeatedly selects a random successor state from the given parent state
        and checks for win or draw conditions until a terminal state is reached.
        """
        board = self.state
        original_board_state = board
        while True:
            moves = self.get_neighbour_moves(level)
            if not moves.size:
                self.state = original_board_state
                return board.check_win()
            self.state = random.choice(moves)
            if (
                    (board.check_win() == 2 and self.check_draw())
                    or board.check_win() == 1
                    or board.check_win() == 0
            ):
                break
            level = level ^ 1
        self.state = original_board_state
        return board.check_win()

    def update(self, result):
        """
        Update the scores and visits of the parent node and its ancestors based on the simulation result.

        Parameters:
        result (int): The result of the simulation (1 for player 1 win, 0 for player 2 win, 2 for draw).

        Returns:
        None
        """
        node = self
        while node is not None:
            if result != 2:
                node.score += (-1) ** (node.level + result)
            node.visits += 1
            node = node.parent
