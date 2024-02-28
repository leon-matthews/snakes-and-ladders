#!/usr/bin/env python3

"""
Silly benchmark which plays many, many solo games of snakes and ladders.

Runs on Python 3.7 and up.

Copyright 2011-2024 Leon Matthews. Released under the Apache 2.0 licence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent import futures
from dataclasses import asdict, dataclass, field
import functools
import json
import math
import os
import random
import sys
import time
from typing import Any, Callable, Dict, List, Iterator, Optional, Tuple


# Python 3.10+
# Game: TypeAlias = List[Tuple[int, int]]
Game = List[Tuple[int, int]]


@dataclass
class BenchmarkResult:
    """
    Results for a benchmark run.

    counts:
        Mapping of game length against number of games.
    elapsed:
        Time in seconds.
    num_games:
        Total number of games played.
    shortest:
        Full roll and position history of shortest game played.
    longest:
        As per `shortest`, but for the longest game.
    """
    counts: Dict[int, int] = field(default_factory=dict)
    elapsed: float = 0.0
    num_games: int = 0
    shortest: Game = field(default_factory=list)
    longest: Game = field(default_factory=list)

    @property
    def rate(self) -> int:
        return round(self.num_games / self.elapsed)

    def __add__(self, other: BenchmarkResult) -> BenchmarkResult:
        """
        Combine two results and create a new one.
        """
        def len_not_empty(value: Game) -> int:
            length = len(value)
            if length == 0:
                return sys.maxsize
            return length

        counts = dict(Counter(self.counts) + Counter(other.counts))
        result = BenchmarkResult(
            counts=counts,
            elapsed=self.elapsed + other.elapsed,
            num_games=self.num_games + other.num_games,
            shortest=min(self.shortest, other.shortest, key=len_not_empty),
            longest=max(self.longest, other.longest, key=len),
        )
        return result


def multiset_median(
    counter: Counter[int],
    *,
    high: bool = False,
    low: bool = False,
) -> float:
    """
    Efficiently determine the median of counter where the keys are numbers.

    Use the same 'mean of middle two' method that the standard library's
    `statistics` package uses.

    Args:
        high:
            Use the high median rather than the 'mean of middle two'. Value
            returned will be in set.
        low:
            As per `high`, but the low median instead.

    Returns:
        Median value.
    """
    if high and low:
        raise ValueError("Only one of the high and low arguments may be true")

    # Find median values
    counter_total = sum(counter.values())   # `counter.total()` in Python 3.10+
    middle = (counter_total + 1) / 2
    lower_pos = int(math.floor(middle))
    upper_pos = int(math.ceil(middle))
    lower_value = upper_value = None
    count = 0

    for key in sorted(counter.keys()):
        count += counter[key]
        if lower_value is None and count >= lower_pos:
            lower_value = key
        if upper_value is None and count >= upper_pos:
            upper_value = key
            break

    if lower_value is None or upper_value is None:
        raise ValueError("Cannot calculate median of empty Counter")

    # Median present, no interpolation needed
    if lower_pos == upper_pos:
        return lower_value

    # Pick your flavour! Middle-of-two, High, or Low median.
    if high:
        return upper_value
    elif low:
        return lower_value
    else:
        return (lower_value + upper_value) / 2


def currency_series(start: Optional[int] = None) -> Iterator[int]:
    """
    Produces a readable series of numbers that is roughly exponential.

        1, 2, 5, 10, 20, 50, 100, 200, etc.

    Grows a little faster than a power of two series, reaching one million
    after 19 iterations, rather than 20.

    Args:
        start:
            Optionally start the series here.

    Returns:
        A generator of ever increasing integers.
    """
    multiplier = 1
    series = (1, 2, 5)
    value: int
    while True:
        for s in series:
            value = s * multiplier
            if start is None or value >= start:
                yield value
        multiplier *= 10


def play_count(num_games: int = 1_000) -> BenchmarkResult:
    """
    Play the given number of solo games of snakes and ladders.

    Args:
        num_games:
            How many games to play. The default takes about a second on my
            slowest computer: a Raspberry Pi Zero.

    Returns:
        A BenchmarkResult containing the shortest and longest games.
    """
    counts: Counter[int] = Counter()
    shortest: Game = []
    longest: Game = []

    start = time.perf_counter()
    for _ in range(num_games):
        moves = snakes_and_ladders()
        num_moves = len(moves)
        counts[num_moves] += 1
        if not shortest or num_moves < len(shortest):
            shortest = moves
        if num_moves > len(longest):
            longest = moves
    elapsed = time.perf_counter() - start

    result = BenchmarkResult(
        counts=counts,
        elapsed=elapsed,
        longest=longest,
        num_games=num_games,
        shortest=shortest,
    )
    return result


def play_time(seconds: int = 2) -> BenchmarkResult:
    """
    Keep playing solo snakes and ladders for at least the given time.

    The goal was to play a round number of games while minimising the time
    keeping overhead.

    Args:
        seconds:
            Play for at least this number of seconds.

    Returns:
        The result of the benchmark.
    """
    minimum = 100
    previous = BenchmarkResult()
    for total_games in currency_series(start=minimum):
        count = total_games - previous.num_games
        result = previous + play_count(count)
        previous = result
        if result.elapsed > seconds:
            break
    return result


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


def snakes_and_ladders() -> Game:
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


def benchmark_multicore(
    num_jobs: int,
    function: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> BenchmarkResult:
    """
    Run given function on multiple cores and combine its results.

    Args:
        num_jobs:
            Number of processes to start. Should be less than or equal to
            the number of CPU cores available.
        function:
            Benchmark function to run. It must return a BenchmarkResult
            object and accept the remaining args and kwargs arguments.

    Returns:
        All of the individual results added together.
    """
    # Submit jobs
    jobs: list[futures.Future[Any]] = []
    with futures.ProcessPoolExecutor(max_workers=num_jobs) as pool:
        for _ in range(num_jobs):
            future = pool.submit(function, *args, **kwargs)
            jobs.append(future)

    # Wait for, and process results
    result = BenchmarkResult()
    for future in futures.as_completed(jobs):
        result += future.result()
    return result


def parse(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Play many, many solo games of Snakes and Ladders'
    )

    # Multicore?
    num_cores = os.cpu_count()
    parser.add_argument(
        '-j',
        default=-1,
        dest="cores",
        nargs='?',
        type=int,
        help=f"Run on multiple cores ({num_cores} found)",
    )

    # JSON output?
    parser.add_argument(
        '--json',
        action='store_true',
        help="Dump detailed results to stdout as JSON",
    )

    # Iterations or seconds?
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-n',
        dest="num_games",
        type=int,
        help="Number of games to play, eg. 100 or 1e6",
    )
    group.add_argument(
        '-s',
        default=10,
        dest="seconds",
        type=int,
        metavar='SECONDS',
        help="Approximate seconds to play for.",
    )
    options = parser.parse_args(args)

    # Adjust core count
    if options.cores is None:
        options.cores = num_cores
    elif options.cores == -1:
        options.cores = 1

    return options


def main(options: argparse.Namespace) -> int:
    # Use stderr for summaries
    print = functools.partial(__builtins__.print, file=sys.stderr)

    # Choose function
    function: Callable[..., Any]
    if options.num_games:
        num_games = int(options.num_games)
        print(f"Playing {num_games:,} games of Snakes & Ladders", end=' ')
        function = play_count
        argument = num_games
    else:
        seconds = int(options.seconds)
        print(
            f"Playing Snakes & Ladders for at least {seconds} seconds", end=' '
        )
        function = play_time
        argument = seconds

    num_jobs = options.cores
    if num_jobs == 1:
        print("with a single process.")
    else:
        print(f"using {num_jobs} processes.")

    # Run benchmark
    result = benchmark_multicore(num_jobs, function, argument)
    elapsed = result.elapsed / num_jobs
    rate = result.num_games / elapsed
    print(f"{result.num_games:,} games finished in ", end=" ")
    print(f"{elapsed:.2f} seconds ({result.elapsed:.2f}s CPU) =", end=" ")
    print(f"{rate:,.0f} games per second")

    median = int(multiset_median(Counter(result.counts), high=True))
    print(
        f"The shortest game took {len(result.shortest)} moves, "
        f"the longest {len(result.longest)}, "
        f"while the median was {median}."
    )

    # JSON?
    if options.json:
        data = asdict(result)
        # Sort counts by game length
        data['counts'] = {k: data['counts'][k] for k in sorted(data['counts'])}
        print(json.dumps(data, indent=4), file=sys.stdout)

    return 0


if __name__ == '__main__':
    options = parse(sys.argv[1:])
    sys.exit(main(options))
