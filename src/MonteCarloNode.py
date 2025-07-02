# monte_carlo_ai.py

import random
import math
import time

class MCTSNode:
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.getValidMoves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.41):
        return max(
            self.children,
            key=lambda child: (child.wins / child.visits) + c_param * math.sqrt(math.log(self.visits) / child.visits)
        )

    def is_terminal_node(self):
        return self.game_state.checkmate or self.game_state.stalemate

    def expand(self):
        move = self.untried_moves.pop()
        self.game_state.makeMove(move)
        child_node = MCTSNode(self.game_state, self, move)
        self.game_state.undoMove()
        self.children.append(child_node)
        return child_node

    def update(self, result):
        self.visits += 1
        self.wins += result

def simulate(game_state):
    temp_state = deepcopy_game_state(game_state)
    while not (temp_state.checkmate or temp_state.stalemate):
        valid_moves = temp_state.getValidMoves()
        if not valid_moves:
            break
        move = random.choice(valid_moves)
        temp_state.makeMove(move)
    if temp_state.checkmate:
        return 1 if not temp_state.whiteToMove else 0
    return 0.5  # Stalemate or no moves = draw

def deepcopy_game_state(gs):
    import copy
    return copy.deepcopy(gs)

def mcts(root_state, max_iterations=1000):
    root_node = MCTSNode(root_state)

    for _ in range(max_iterations):
        node = root_node
        state = deepcopy_game_state(root_state)

        # Selection
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
            state.makeMove(node.move)

        # Expansion
        if node.untried_moves:
            node = node.expand()
            state.makeMove(node.move)

        # Simulation
        result = simulate(state)

        # Backpropagation
        while node is not None:
            node.update(result)
            node = node.parent

    best_child = max(root_node.children, key=lambda c: c.visits)
    return best_child.move