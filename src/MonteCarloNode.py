import copy
import math

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = copy.deepcopy(state)
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = self.state.getValidMoves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal_node(self):
        return self.state.checkmate or self.state.stalemate

    def expand(self):
        move = self.untried_moves.pop()
        next_state = copy.deepcopy(self.state)
        next_state.makeMove(move)
        child_node = MCTSNode(next_state, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def best_child(self, exploration_constant=1.41):
        return max(
            self.children,
            key=lambda c: (c.wins / c.visits) + exploration_constant * math.sqrt(math.log(self.visits) / c.visits)
            if c.visits > 0 else float("inf")
        )

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(-result)
