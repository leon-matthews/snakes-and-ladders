#!/usr/bin/env python3
"""
Build plots for Snakes and ladders article.
"""

import argparse
import json
from pathlib import Path
from pprint import pprint as pp
import sys
from typing import Any, TypeAlias

import matplotlib.pyplot as pyplot                          # type: ignore
import matplotlib.ticker as mtick                           # type: ignore


Counts: TypeAlias = dict[str, list[int]]
JSON: TypeAlias = dict[str, Any]


def calculate_mean(counts: Counts) -> float:
    """
    Calculate the mean game length.
    """
    total_count = 0
    total_length = 0
    for length, count in zip(counts['x'], counts['y'], strict=True):
        total_count += count
        total_length += length * count

    mean = total_length / total_count
    return mean


def calculate_mode(counts: Counts) -> float:
    greatest = 0
    mode = 0
    for length, count in zip(counts['x'], counts['y'], strict=True):
        if count > greatest:
            mode = length
            greatest = count
    return mode


def calculate_total(counts: Counts) -> int:
    """
    Count the total number of games played.
    """
    total = sum(length for length in counts['y'])
    return total


def get_counts(data: JSON) -> Counts:
    """
    Extract parallel x and y arrays from JSON.
    """
    x = []
    y = []
    for length, count in data['counts'].items():
        length = int(length)
        x.append(length)
        y.append(count)
    return {'x': x, 'y': y}


def plot(counts: Counts, limit: int|None = None) -> None:
    """
    Build and show/save Matplotlib plot.

    Args:
        counts:
            Parallel arrays of counts and frequencies.
        limit:
            Max game length to show, ie. 100

    Returns:
        None
    """
    # Convert game length to percentages, enforce limit
    total_games = calculate_total(counts)
    x = []
    y = []
    for length, count in zip(counts['x'], counts['y'], strict=True):
        percentage = (count / total_games)
        x.append(length)
        y.append(percentage)
        if limit is not None and length >= limit:
            break

    # Plot game length against frequency
    figure = pyplot.figure()
    axes = figure.add_subplot(1, 1, 1)

    axes.set_title("Frequency vs Game length")
    axes.set_ylabel('Percentage of Games')
    axes.set_xlabel('Length')
    axes.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=1))
    axes.plot(x, y)

    # Add mean line
    mean = calculate_mean(counts)
    axes.axvline(
        x=mean, color='green', linestyle='--', linewidth=1, label=f"Mean={mean:.1f}",
    )

    # Add median line
    # Calculated in the main simulation.
    axes.axvline(
        x=33, color='red', linestyle='--', linewidth=1, label='Median=33.0',
    )

    # Add mode line
    mode = calculate_mode(counts)
    axes.axvline(
        x=mode, color='blue', linestyle='--', linewidth=1, label=f"Mode={mode:.1f}",
    )

    axes.legend(loc="upper right")
    pyplot.show()


def read_json(path: Path) -> JSON:
    """
    Read JSON data into dictionary.
    """
    with open(path, 'rt') as fp:
        data = json.load(fp)
    assert isinstance(data, dict)
    return data


def parse(args: list[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Plot data from Snakes & Ladders script'
    )
    parser.add_argument(
        dest='path',
        metavar='JSON',
        help="Data from Snakes & Ladders script",
    )
    parser.add_argument(
        dest='image',
        metavar='IMAGE',
        nargs='?',
        help="Image file to write plot into",
    )
    parser.add_argument(
        '-l',
        '--limit',
        metavar='',
        type=int,
        help="Don't plot game lengths longer than limit",
    )
    options = parser.parse_args(args)
    return options


def main(options: argparse.Namespace) -> int:
    """
    Script entry point
    """
    pp(options)
    path = Path(options.path)
    data = read_json(path)
    counts = get_counts(data)
    plot(counts, limit=options.limit)
    return 0


if __name__ == '__main__':
    options = parse(sys.argv[1:])
    sys.exit(main(options))
