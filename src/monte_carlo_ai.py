import random
import math
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import copy

CHECKMATE = 1000
STALEMATE = 0
MAX_SIM_THREADS = 8  # Adjustable based on CPU

class MCTSNode:
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = copy.deepcopy(game_state)
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = self.game_state.getValidMoves()

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

def get_piece_value(piece):
    if piece == "--": return 0
    return {
        "pawn": 10, "knight": 30, "bishop": 30,
        "rook": 50, "queen": 90, "king": 900
    }.get(piece.split()[-1], 0)

def move_heuristic(state, move):
    score = 0
    if move.pieceCaptured != "--":
        score += max(0, get_piece_value(move.pieceCaptured) - get_piece_value(move.pieceMoved) + 10)

    if move.pieceMoved.endswith("pawn") and (move.endRow in [0, 7]):
        score += 20

    if move.endCol in [2, 3, 4, 5] and move.endRow in [2, 3, 4, 5]:
        score += 2

    if len(state.moveLog) < 12:
        if move.pieceMoved.endswith("knight"): score += 3
        elif move.pieceMoved.endswith("bishop"): score += 2
        elif move.pieceMoved.endswith("queen"): score -= 2

    if getattr(move, "isCastleMove", False):
        score += 6

    if move.pieceMoved.endswith("pawn") and abs(move.startRow - move.endRow) == 2:
        score += 1

    try:
        state.makeMove(move)
        next_moves = state.getValidMoves()
        threats = {(m.endRow, m.endCol) for m in next_moves if m.pieceCaptured != "--"}
        state.undoMove()
        score += len(threats) * 0.5
    except Exception as e:
        print(f"[!] Error during heuristic simulation: {e}")
        state.undoMove()

    return score

def select_best_move_parallel(state, moves):
    with ThreadPoolExecutor(max_workers=min(len(moves), MAX_SIM_THREADS)) as executor:
        scores = list(executor.map(lambda m: move_heuristic(state, m), moves))
    return moves[scores.index(max(scores))]

def simulate_guided_game(state):
    max_turns = 7
    try:
        for _ in range(max_turns):
            if state.checkmate or state.stalemate:
                break
            moves = state.getValidMoves()
            if not moves:
                break
            move = select_best_move_parallel(state, moves)
            state.makeMove(move)
    except Exception as e:
        print(f"[!] Error in guided simulation: {e}")

    if state.checkmate:
        return 1 if not state.whiteToMove else -1
    return 0.5

def run_single_iteration(initial_state):
    root = MCTSNode(copy.deepcopy(initial_state))
    node = root

    while node.is_fully_expanded() and node.children:
        node = node.best_child()
        node.game_state.makeMove(node.move)

    if not node.is_terminal_node() and node.untried_moves:
        node = node.expand()
        node.game_state.makeMove(node.move)

    result = simulate_guided_game(node.game_state)

    while node is not None:
        node.update(result)
        node = node.parent

    return root

def merge_nodes(master, other):
    for child in other.children:
        match = next((c for c in master.children if c.move == child.move), None)
        if match:
            match.wins += child.wins
            match.visits += child.visits
        else:
            master.children.append(child)

from concurrent.futures import ProcessPoolExecutor  # umesto ThreadPoolExecutor

def parallel_mcts(gs, iterations=300, max_workers=4):
    print(f"[MCTS] Starting {iterations} iterations with {max_workers} workers (PROCESS-based)...")
    start = time.time()
    master = MCTSNode(copy.deepcopy(gs))

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_single_iteration, gs) for _ in range(iterations)]
        for i, future in enumerate(futures):
            try:
                merge_nodes(master, future.result(timeout=60))
            except Exception as e:
                print(f"[!] Simulation {i} failed: {e}")
                traceback.print_exc()

    if not master.children:
        print("[!] No valid children found.")
        return None

    best = max(master.children, key=lambda c: c.visits)
    print(f"[\u2713] Best move selected in {time.time() - start:.2f} seconds: {best.move}")
    return best.move


