import sys
import math
import copy
import random

import pygame as pygame

from Board import Board
from MCTSTreeNode import MCTSTreeNode


BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
# Constants
Rows = 6
Cols = 5


def human_player(current_node, board, turn, level, col):
    """
    Simulates a human player's move in the game.

    Parameters:
    current_node (MCTSTreeNode): The current node in the game tree.
    board (list): The current state of the game board represented as a 2D list.
    turn (int): The player number (0 for player 2, 1 for player 1).
    level (int): The level of the current node in the game tree (0 for player 2, 1 for player 1).
    col (int): The column where the human player wants to place their piece.

    Returns:
    MCTSTreeNode: A new node representing the state of the game board after the human player's move.
    """
    board_cpy = copy.deepcopy(board)
    row = 0
    while row < Rows - 1 and board[row, col] == 2:
        row += 1
    if board[row, col] != 2:
        row -= 1
    board_cpy[row, col] = turn ^ 1
    new_board = Board()
    new_board.set_whole_board(board_cpy)
    return MCTSTreeNode(new_board, current_node, turn ^ 1, level ^ 1)


def mcts_n(parent_node, n):
    """
    Performs a Monte Carlo Tree Search (MCTS) for a specified number of iterations.

    Parameters:
    parent_node (MCTSTreeNode): The root node of the game tree.
    n (int): The number of iterations for the MCTS.

    Returns:
    MCTSTreeNode: The selected child node from the parent node based on the MCTS algorithm.

    The function performs MCTS by repeatedly selecting a child node based on the UCB1 formula,
    expanding the game tree by selecting a random successor state, simulating a game from
    the selected successor state, and updating the scores and visits of the nodes in the
    game tree. The function continues this process until the specified number of iterations
    is reached or a terminal state is reached.
    """
    initial_node = copy.deepcopy(parent_node)
    while n > 0 and parent_node.state.check_win() == 2 and not parent_node.check_draw():
        if len(parent_node.Poss_Child) and random.uniform(0, 1) >= 0:
            parent_node = parent_node.expansion()
            result = parent_node.simulation(parent_node.level)
            parent_node.update(result)
            parent_node = initial_node
            n = n - 1
        else:
            parent_node = parent_node.selection()

    lists = []
    parent_node = initial_node
    for child_node in parent_node.children:
        if child_node.state.check_win() == parent_node.turn:
            return child_node
        if not lists:
            lists.append(child_node)
        else:
            if lists[0].visits < child_node.visits:
                lists = [child_node]
            elif lists[0].visits == child_node.visits:
                lists.append(child_node)
    if lists:
        child = lists[0]
    else:
        child = MCTSTreeNode(
            random.choice(initial_node.state.GetNeighbourMoves(initial_node.level)),
            initial_node,
            initial_node.turn ^ 1,
            initial_node.level ^ 1,
        )
    max_score = -10
    for i in lists:
        if i.score > max_score:
            child = i
            max_score = i.score
    return child


def game_driver(screen, square_size, width, radius):
    """
    The main driver function for the game. Handles user input, game logic, and rendering.

    Parameters:
    screen (pygame.Surface): The surface object representing the game window.
    square_size (int): The size of each square on the game board.
    width (int): The width of the game window.
    radius (int): The radius of the circles representing the game pieces.

    Returns:
    None
    """

    def handle_quit_event():
        """
        Handles the QUIT event, which occurs when the user closes the game window.
        Exits the game when the QUIT event is detected.
        """
        for pygame_event in pygame.event.get(pygame.QUIT):
            if pygame_event.type == pygame.QUIT:
                sys.exit()

    def handle_mouse_motion(event_local, turn_local):
        """
        Handles the MOUSE MOTION event, which occurs when the mouse is moved within the game window.
        Draws a circle representing the current player's piece at the mouse's position.

        Parameters:
        event_local (pygame.event.Event): The MOUSE MOTION event object.
        turn_local (int): The current player's turn (0 for player 2, 1 for player 1).
        """
        pygame.draw.rect(screen, BLACK, (0, 0, width, square_size))
        px = event_local.pos[0]
        color = RED if turn_local == 0 else YELLOW
        pygame.draw.circle(screen, color, (px, int(square_size / 2)), radius)
        pygame.display.update()

    def handle_mouse_button_down(event_local, current_node_local, turn_local):
        """
        Handles the MOUSE BUTTON DOWN event, which occurs when a mouse button is pressed.
        Determines the column where the current player wants to place their piece and
        updates the game state accordingly.

        Parameters:
        event_local (pygame.event.Event): The MOUSE BUTTON DOWN event object.
        current_node_local (MCTSTreeNode): The current node in the game tree.
        turn_local (int): The current player's turn (0 for player 2, 1 for player 1).

        Returns:
        MCTSTreeNode: The new node representing the state of the game board after the current player's move.
        """
        px = event_local.pos[0]
        col = int(math.floor(px / square_size))
        if turn_local == 0:
            return human_player(
                current_node_local,
                current_node_local.state.get_board(),
                turn_local,
                current_node_local.level,
                col,
            )
        else:
            return mcts_n(current_node, 200)

    def draw_current_board(current_state_local):
        """
        Draws the current state of the game board on the screen.

        Parameters:
        current_state_local (Board): The current state of the game board.
        """
        draw_board(current_state_local.get_board(), screen, square_size, radius)

    turn = 0
    board = Board()
    current_node = MCTSTreeNode(board, None, 0, 0)
    current_state = current_node.state

    while current_state.check_win() == 2 and not current_node.check_draw():
        handle_quit_event()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event, turn)
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_node = handle_mouse_button_down(event, current_node, turn)
                current_state = current_node.state
                turn = turn ^ 1
                draw_current_board(current_state)

    pygame.time.wait(3000)


def draw_board(board, screen, SQ_SIZE, RADIUS):
    """
    Draws the current state of the game board on the screen.

    Parameters:
    board (numpy.ndarray): The current state of the game board represented as a 2D numpy array.
    screen (pygame.Surface): The surface object representing the game window.
    SQ_SIZE (int): The size of each square on the game board.
    RADIUS (int): The radius of the circles representing the game pieces.

    Returns:
    None
    """
    for c in range(Cols):
        for r in range(Rows):
            # Draw a blue rectangle to represent an empty cell
            pygame.draw.rect(
                screen, BLUE, (c * SQ_SIZE, r * SQ_SIZE + SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )
            # Draw a black circle to represent a piece of player 2
            if board[r, c] == 2:
                pygame.draw.circle(
                    screen,
                    BLACK,
                    (
                        int(c * SQ_SIZE + SQ_SIZE / 2),
                        int(r * SQ_SIZE + SQ_SIZE + SQ_SIZE / 2),
                    ),
                    RADIUS,
                )
            # Draw a red circle to represent a piece of player 1
            if board[r, c] == 1:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(c * SQ_SIZE + SQ_SIZE / 2),
                        int(r * SQ_SIZE + SQ_SIZE + SQ_SIZE / 2),
                    ),
                    RADIUS,
                )
            # Draw a yellow circle to represent a piece of player 0
            if board[r, c] == 0:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(c * SQ_SIZE + SQ_SIZE / 2),
                        int(r * SQ_SIZE + SQ_SIZE + SQ_SIZE / 2),
                    ),
                    RADIUS,
                )
    # Update the display to show the changes
    pygame.display.update()


def main():
    pygame.init()
    ASSIZE = 100
    width = Cols * ASSIZE
    height = (Rows + 1) * ASSIZE
    size = (width, height)
    RADIUS = int(ASSIZE / 2 - 3)
    screen = pygame.display.set_mode(size)
    pygame.display.update()
    game_driver(screen, ASSIZE, width, RADIUS)


if __name__ == "__main__":
    main()
