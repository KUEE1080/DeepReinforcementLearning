#!/usr/bin/env python
# coding: utf-8

"""Go library made with pure Python.

This library offers a variety of Go related classes and methods.

There is a companion module called 'goban' which serves as a front-end
for this library, forming a fully working go board together.

"""

__author__ = "Aku Kotkavuo <aku@hibana.net>"
__version__ = "0.1"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Stone(object):
    def __init__(self, board, point, color):
        """Create and initialize a stone.

        Arguments:
        board -- the board which the stone resides on
        point -- location of the stone as a tuple, e.g. (3, 3)
                 represents the upper left hoshi
        color -- color of the stone

        """
        self.board = board
        self.point = point
        self.color = color
        self.group = self.find_group()


    def remove(self):
        """Remove the stone from board."""
        self.group.stones.remove(self)
        del self

    @property
    def neighbors(self):
        """Return a list of neighboring points."""
        neighboring = [(self.point[0] - 1, self.point[1]),
                       (self.point[0] + 1, self.point[1]),
                       (self.point[0], self.point[1] - 1),
                       (self.point[0], self.point[1] + 1)]
        for point in neighboring:
            if not 0 < point[0] < 20 or not 0 < point[1] < 20:
                neighboring.remove(point)
        return neighboring

    @property
    def liberties(self):
        """Find and return the liberties of the stone."""
        liberties = self.neighbors
        stones = self.board.search(points=self.neighbors)
        for stone in stones:
            liberties.remove(stone.point)
        return liberties

    # go.py 안에 있는 Stone 클래스 생성자에서 딱 한번 쓰이는 함수
    def find_group(self):
        """Find or create a group for the stone."""
        groups = []
        stones = self.board.search(points=self.neighbors)
        for stone in stones:
            if stone.color == self.color and stone.group not in groups:
                groups.append(stone.group)
        if not groups:
            group = Group(self.board, self)
            return group
        else:
            if len(groups) > 1:
                for group in groups[1:]:
                    groups[0].merge(group)
            groups[0].stones.append(self)
            return groups[0]

    def __str__(self):
        """Return the location of the stone, e.g. 'D17'."""
        return 'ABCDEFGHJKLMNOPQRST'[self.point[0]-1] + str(20-(self.point[1]))


"""Group 클래스가 쓰이는 경우는 오직 find_group 함수 안 밖에 없으나, 저게 엄청 많이 쓰여서 고루고루 쓰인다."""
"""이건 도대체 용도가 뭐임..??"""
class Group(object):
    def __init__(self, board, stone):
        """Create and initialize a new group.

        Arguments:
        board -- the board which this group resides in
        stone -- the initial stone in the group

        """
        self.board = board
        self.board.groups.append(self)
        self.stones = [stone]
        self.liberties = None

    def merge(self, group):
        """Merge two groups.

        This method merges the argument group with this one by adding
        all its stones into this one. After that it removes the group
        from the board.

        Arguments:
        group -- the group to be merged with this one

        """
        for stone in group.stones:
            stone.group = self
            self.stones.append(stone)
        self.board.groups.remove(group)
        del group

    def remove(self):
        """Remove the entire group."""
        while self.stones:
            self.stones[0].remove()
        self.board.groups.remove(self)
        del self

    def update_liberties(self):
        """Update the group's liberties.

        As this method will remove the entire group if no liberties can
        be found, it should only be called once per turn.

        """
        liberties = []
        for stone in self.stones:
            for liberty in stone.liberties:
                liberties.append(liberty)
        self.liberties = set(liberties)
        if len(self.liberties) == 0:
            self.remove()

    def __str__(self):
        """Return a list of the group's stones as a string."""
        return str([str(stone) for stone in self.stones])


class Board(object):
    def __init__(self):
        """Create and initialize an empty board."""
        self.groups = []  # self.board.groups.append(self) 코드에서 데이터가 할당된다.
        self.next = BLACK

    def search(self, point=None, points=[]):
        """Search the board for a stone.

        The board is searched in a linear fashion, looking for either a
        stone in a single point (which the method will immediately
        return if found) or all stones within a group of points.

        Arguments:
        point -- a single point (tuple) to look for
        points -- a list of points to be searched

        used int connect6.py and liberties function written here

        """
        stones = []
        for group in self.groups:
            for stone in group.stones:
                if stone.point == point and not points:  # 육목에서는 필요없는 코드
                    return stone
                if stone.point in points:  # 사용자가 돌이 위치한 부분에 클릭한 경우
                    stones.append(stone)
        return stones

    def turn(self, move):
        """1st turn: BLACK puts one stone; else: WHITE & Black put 2 stones, and so on..."""
        if move % 4 == 0 or move % 4 == 1:
            return BLACK
        else:
            return WHITE
