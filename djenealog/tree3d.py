"""
plot all related people on a 2d grid.

Yes, this is called 3d, because it will become 3d at some point.

And also, for now it is a square grid, but it would be better with hex
"""

from collections.abc import Iterator
from random import shuffle

from .models import Individu, Naissance


def plot(v):
    for x in range(-20, 20):
        for y in range(-20, 20):
            print("X" if (x, y) in v else " ", end="")
        print()


def around(x: int, y: int) -> Iterator[(int, int)]:
    i = 0
    while True:
        i += 1
        r = range(-i, i + 1)
        v = [
            *[(x + i, y + o) for o in r],
            *[(x - i, y + o) for o in r],
            *[(x + o, y + i) for o in r],
            *[(x + o, y - i) for o in r],
        ]
        shuffle(v)
        yield from v


class Grid:
    def __init__(self, first: Individu):
        self.grid = {(0, 0): first}
        self.individus = {first: (0, 0)}

    def next(self, x: int, y: int) -> (int, int):
        for a, b in around(x, y):
            if (a, b) not in self.grid:
                return (a, b)
        err = f"can't find something close to {x} {y}"
        raise RuntimeError(err)

    def add(self, i: Individu, j: Individu):
        x, y = self.individus[i]
        a, b = self.next(x, y)
        self.grid[(a, b)] = j
        self.individus[j] = (a, b)


def tree():
    first = sorted(Naissance.objects.exclude(y=None), key=lambda n: n.date())[0].inst
    grid = Grid(first)
    todo = [first]
    epoch = 0
    while todo:
        print(f"{epoch=}: {len(todo)=}, {len(grid.individus)=}")
        epoch += 1
        next_todo = []
        for i in todo:
            for j in i.close_ones():
                if j is None:
                    continue  # TODO
                if j not in grid.individus:
                    grid.add(i, j)
                    next_todo.append(j)
        todo = next_todo
    return grid
