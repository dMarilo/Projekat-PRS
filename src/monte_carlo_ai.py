import time
import copy
import random
from MonteCarloNode import MCTSNode

CHECKMATE = 1000
STALEMATE = 0

def mcts_best_move(gs, iterations=100):
    root = MCTSNode(gs)
    for _ in range(iterations):
        node = root

        while not node.is_terminal_node() and node.is_fully_expanded():
            node = node.best_child()


        if not node.is_terminal_node() and not node.is_fully_expanded():
            node = node.expand()


        result = simulate_random_game(copy.deepcopy(node.state))


        node.backpropagate(result)


    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move

def simulate_random_game(state):
    while not state.checkmate and not state.stalemate:
        moves = state.getValidMoves()
        if not moves:
            break
        move = random.choice(moves)
        state.makeMove(move)

    if state.checkmate:
        return 1 if not state.whiteToMove else -1
    return 0
