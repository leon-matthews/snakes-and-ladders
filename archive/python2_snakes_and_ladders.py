#!/usr/bin/env python3

"""
Stripped down version of Snakes & Ladders game with maximal compatibility.

Copyright 2011-2024 Leon Matthews. Released under the Apache 2.0 licence.
"""

import random
import time


# Run on Python3 (without any dependencies)
try:
    xrange
except NameError:
    xrange = range


SNAKES_AND_LADDERS = {
    # Ladders
    1: 38,
    4: 14,
    9: 31,
    21: 42,
    28: 84,
    36: 44,
    51: 67,
    71: 91,
    80: 100,

    # Snakes
    98: 78,
    95: 75,
    93: 73,
    87: 24,
    64: 60,
    62: 19,
    56: 53,
    49: 11,
    48: 26,
    16: 6,
}


def snakes_and_ladders():
    """
    Play a solo game of snakes and ladders.

    Snakes and ladders is a horrible game. The conclusion is totally random,
    with zero skill involved. With kids, the only audience credible enough to
    want to play it, there is way too much drama, especially with the last
    snake. Tears often result.

    However, it's also fascinating. It has been around is some form or other
    for almost 2,000 years. If you're unlucky enough a game can last forever.
    While torturing my computers with this silly program, they've played sole
    games lasting more than 500 dice rolls.

    Standard rules: you need the exact roll to land on 100, do not move if roll
    overshoots it.

    Generates and returns a list of moves taken to win the game. Each move is
    a 2-tuple of integers: the dice roll, then the square you end up on. For
    For example, one of the two possible shortest, 7 move games is:

        [(4, 14), (6, 20), (6, 26), (2, 84), (5, 89), (5, 94), (6, 100)]

    See:
        https://en.wikipedia.org/wiki/Snakes_and_ladders

    Returns:
        List of moves taken for the game.
    """
    moves = []
    place = 0
    while True:
        # Roll the dice
        # roll = random.randint(1, 6)
        roll = int(6 * random.random()) + 1
        landed = place + roll

        if landed > 100:
            # Too high, ignore
            pass
        else:
            # Special move or as rolled
            place = SNAKES_AND_LADDERS.get(landed, landed)

        moves.append((roll, place))

        # Won? Require exact roll.
        if place == 100:
            return moves


if __name__ == '__main__':
    num_games = int(1e6)
    start = time.time()
    for _ in xrange(num_games):
        game = snakes_and_ladders()
    print("Played {:,} games in {:.3f} seconds".format(
            num_games, time.time() - start))
