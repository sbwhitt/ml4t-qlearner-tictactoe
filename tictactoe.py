import time
import random as rand
import numpy as np
from QLearner import QLearner

LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8), # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8), # cols
    (0, 4, 8), (2, 4, 6)             # diags
]

def to_board(state: int) -> str:
    return str(np.base_repr(state, base=3)).zfill(9)

def to_state(board: str) -> int:
    '''
    base 3 str to base 10 int
    '''
    return sum([
        int(c)*(3**(len(board)-(i+1))) for i, c in enumerate(board)
    ])

def outcome(state: int) -> int:
    '''
    0 = active game, 1 = player 1 win, 2 = player 2 win, 3 = draw
    '''
    board = to_board(state)
    # looking for complete lines, wins
    for l in LINES:
        line = board[l[0]] + board[l[1]] + board[l[2]]
        if line == "111": return 1
        if line == "222": return 2
    # looking for active game
    for l in LINES:
        line = board[l[0]] + board[l[1]] + board[l[2]]
        if not (("1" in line) and ("2" in line)): return 0
    # it's a draw
    return 3

def reward(out: int) -> int:
    match (out):
        case 1: return 1  # win
        case 2: return -5 # lose
        case 3: return -1 # draw
        case 0: return -1 # active game

def place_opp(board: str) -> str:
    '''
    places randomly some of the time and tries strategic points otherwise
    '''
    free = []
    for i in range(len(board)):
        if board[i] == "0": free.append(i)
    # illegal move
    if not free: return board
    action = None
    for l in LINES:
        # choose 'strategic' opponent move some proportion of the time if possible
        # 'strategic' just means placing an O in a line that already has 2 matching moves
        # either blocks the opponent or completes a line of three to win
        if rand.random() < 0.5: break
        a, b, c = l
        if (board[a] == board[b]) and (board[c] == "0"):
            action = c
            break
        elif (board[a] == board[c]) and (board[b] == "0"):
            action = b
            break
        elif (board[b] == board[c]) and (board[a] == "0"):
            action = a
            break
    # random free space
    action = rand.choice(free) if action == None else action
    return board[:action] + "2" + board[action+1:]

def update_board(state: int, action: int, training=False, player=1) -> str:
    board = to_board(state)
    if board[action] != "0": return board
    board = board[:action] + str(player) + board[action+1:] # place player
    if training:
        return place_opp(board)
    else:
        return board

def print_board(board: str) -> None:
    symbols = { "0": " ", "1": "X", "2": "O" }
    print()
    print(" | ".join([symbols[t] for t in board[:3]]))
    print("---------")
    print(" | ".join([symbols[t] for t in board[3:6]]))
    print("---------")
    print(" | ".join([symbols[t] for t in board[6:]]))
    print()

def train(learner: QLearner, epochs=500, verbose=False) -> None:
    '''
    learner player = 1 (X)
    opponent = 2 (O)
    '''
    start = time.time()
    limit = 5000
    wins, losses, draws = 0, 0, 0
    for epoch in range(1, epochs + 1):
        count = 0
        epoch_reward = 0
        board = "000000000"
        state = to_state(board)
        action = learner.querysetstate(state)
        out = 0
        while (out == 0) and (count < limit):
            board = update_board(state, action, training=True)
            state = to_state(board)
            out = outcome(state)
            step_reward = reward(out)
            action = learner.query(state, step_reward)
            epoch_reward += step_reward
            count += 1
        wins += 1 if out == 1 else 0
        losses += 1 if out == 2 else 0
        draws += 1 if out == 3 else 0
        # if verbose:
        #     b = update_board(state, action)
        #     print_board(b)
        #     print(f"{epoch}, avg. reward: {epoch_reward / count}")
        #     print()
    elapsed = time.time() - start
    if verbose:
        print(f"training took {elapsed} seconds")
        print(f"total wins: {wins} out of {epochs}, {(wins/epochs)*100}%")
        print(f"total losses: {losses} out of {epochs}, {(losses/epochs)*100}%")
        print(f"total draws: {draws} out of {epochs}, {(draws/epochs)*100}%")


VALID_MOVES = [i for i in range(9)]

def player_turn(board: str) -> str:
    print("player turn")
    new_board = board
    while new_board == board:
        player_action = input(">")
        try:
            player_action = int(player_action)
        except ValueError as _:
            print("invalid move")
            continue
        if player_action not in VALID_MOVES:
            print("invalid move")
            continue
        new_board = update_board(to_state(board), player_action, player=2)

    return new_board

def learner_turn(board: str, out: int) -> str:
    new_board = board
    print("robot turn")
    while new_board == board:
        learner_action = learner.query(to_state(board), reward(out))
        new_board = update_board(to_state(board), learner_action, player=1)
    return new_board

def play(learner: QLearner) -> None:
    start_board = "000000000"
    print("\n--- new game ---")
    learner_action = learner.querysetstate(to_state(start_board))
    # learner always goes first and is Xs
    board = update_board(to_state(start_board), learner_action, player=1)
    print_board(board)
    out = outcome(to_state(board))
    while out == 0:
        board = player_turn(board)
        print_board(board)

        out = outcome(to_state(board))
        if out != 0: break

        board = learner_turn(board, out)
        print_board(board)
        out = outcome(to_state(board))

    print("game over")
    match (out):
        case 0: print("cancelled")
        case 1: print("robot wins")
        case 2: print("player wins")
        case 3: print("draw")

if __name__ == "__main__":
    num_states = int(3**9) # 3 possibilities for each of the 9 tiles
    num_actions = 9        # place an X in one of 9 tiles

    dyna = False
    epochs = 150000
    verbose = True

    learner = QLearner(
        num_states=num_states,
        num_actions=num_actions,
        alpha=0.2,
        gamma=0.9,
        rar=0.5,
        radr=0.99,
        dyna=100,
        verbose=False,
    ) if dyna else QLearner(
        num_states=num_states,
        num_actions=num_actions,
        alpha=0.2,
        gamma=0.9,
        rar=0.9,
        radr=0.999,
        dyna=0,
        verbose=False,
    )

    train(learner, epochs=epochs, verbose=verbose)

    while 1:
        play(learner)
