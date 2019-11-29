#!/usr/bin/env python
# coding: utf-8

"""Goban made with Python, pygame and go.py.

This is a front-end for my go library 'go.py', handling drawing and
pygame-related activities. Together they form a fully working goban.


______________________Lee Dong Jae___________________________

It used to be a go game. However, It is now modified as connect6 game for testing out
the artificial intelligence.

"""

__author__ = "Original: Aku Kotkavuo <akg@hibana.net>, Modified by Lee Dong Jae <exponentialeecode@gmail.com>"
__version__ = "1.0"

import pygame
from sys import exit

import AI_version1 as AI
import AI_version2 as AI2

BACKGROUND = 'images/ramin.jpg'
BOARD_SIZE = (820, 820)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

_NO_STONE = 0
_BLACK = 1
_WHITE = 2

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

        self.coords = (5 + self.point[0] * 40, 5 + self.point[1] * 40)
        self.draw()  # Stone 클래스가 호출되자마자 화면에 그리게 설계함.

    def draw(self):
        """Draw the stone as a circle."""
        pygame.draw.circle(screen, self.color, self.coords, 20, 0)
        pygame.display.update()

    def remove(self):
        """Remove the stone from board."""
        blit_coords = (self.coords[0] - 20, self.coords[1] - 20)
        area_rect = pygame.Rect(blit_coords, (40, 40))
        screen.blit(background, blit_coords, area_rect)
        pygame.display.update()
        # super(Stone, self).remove()

    def __str__(self):
        """Return the location of the stone, e.g. 'D17'."""
        return 'ABCDEFGHIJKLMNOPQRST'[self.point[0]-1] + str(self.point[1])


class Board(object):

    """
    0: NO STONE
    1: WHITE
    2: BLACK
    """
    stone_set = [[_NO_STONE] * 19 for i in range(19)]
    black_stone_order = [[_NO_STONE] * 19 for i in range(19)]
    white_stone_order = [[_NO_STONE] * 19 for i in range(19)]

    black_cnt = 1
    white_cnt = 1

    def __init__(self):
        """Create and initialize a new group.

        Arguments:
        board -- the board which this group resides in
        stone -- the initial stone in the group

        """
        self.liberties = None

        self.outline = pygame.Rect(45, 45, 720, 720)  # 바깥 굵은 줄 정보 선언
        self.draw()

    def draw(self):
        """Draw the board to the background and blit it to the screen.

        The board is drawn by first drawing the outline, then the 19x19
        grid and finally by adding hoshi to the board. All these
        operations are done with pygame's draw functions.

        This method should only be called once, when initializing the
        board.

        """
        pygame.draw.rect(background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(18):
            for j in range(18):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(background, BLACK, rect, 1)
        for i in range(3):
            for j in range(3):
                coords = (165 + (240 * i), 165 + (240 * j))
                pygame.draw.circle(background, BLACK, coords, 5, 0)
        screen.blit(background, (0, 0))
        pygame.display.update()

    def turn(self, move):
        """1st turn: BLACK puts one stone; else: WHITE & BLACK put 2 stones, and so on..."""
        if move % 4 == 0 or move % 4 == 1:
            return BLACK
        else:
            return WHITE

    def update_stone_set(self, added_stone):
        coors = str(added_stone)
        x = ord(coors[0]) - 65  # A,B,C,D,E,...
        y = int(coors[1:]) - 1  # 1,2,...

        if added_stone.color == BLACK:
            self.stone_set[y][x] = _BLACK
        else:
            self.stone_set[y][x] = _WHITE

    def update_stone_order(self, added_stone):
        coors = str(added_stone)
        x = ord(coors[0]) - 65  # A,B,C,D,E,...
        y = int(coors[1:]) - 1  # 1,2,...

        if added_stone.color == BLACK:
            self.black_stone_order[y][x] = self.black_cnt
            self.black_cnt += 1
        else:
            self.white_stone_order[y][x] = self.white_cnt
            self.white_cnt += 1

    def print_stone_set(self):
        for i in range(19):
            print(self.stone_set[i])

    def win(self):
        """
        채점 기준: 6목만 인정하며, 7목 8목은 실격패다.
        현재 7목 이상이 판정이 안된다. 일단 보류 중인데, max_cnt를 구한 다음, 이게 6 초과면 실격 처리.
        물론 저 print_result 함수도 반복문 밖에서 대기해야한다.
        """

        # VERTICAL
        for x in range(19):
            cnt = 0
            _color = _BLACK  # 딱히 상관은 없음
            for i in range(19):
                stone_val = self.stone_set[i][x]
                _color, cnt = self.count_six(stone_val, _color, cnt)

                exit_req = self.print_result(_color, cnt)
                if exit_req:
                    break

        # HORIZONTAL
        for y in range(19):
            cnt = 0
            _color = _BLACK
            for i in range(19):
                stone_val = self.stone_set[y][i]
                _color, cnt = self.count_six(stone_val, _color, cnt)

                exit_req = self.print_result(_color, cnt)
                if exit_req:
                    break

        # DIAGONAL (L -> R)
        for i in range(14): # 여기 부분 체크!
            cnt = 0
            _color = _BLACK
            for j in range(19 - i):
                stone_val = self.stone_set[i + j][0 + j]
                _color, cnt = self.count_six(stone_val, _color, cnt)

                exit_req = self.print_result(_color, cnt)
                if exit_req:
                    break

        for i in range(1, 14):
            cnt = 0
            _color = _BLACK
            for j in range(19 - i):
                stone_val = self.stone_set[0 + j][i + j]
                _color, cnt = self.count_six(stone_val, _color, cnt)

                exit_req = self.print_result(_color, cnt)
                if exit_req:
                    break

        # DIAGONAL (R -> L)
        for i in range(14):
            cnt = 0
            _color = _BLACK
            for j in range(19 - i):
                stone_val = self.stone_set[j][18 - i - j]
                _color, cnt = self.count_six(stone_val, _color, cnt)

                exit_req = self.print_result(_color, cnt)
                if exit_req:
                    break

        for i in range(1, 14):
            for j in range(19 - i):
                stone_val = self.stone_set[i + j][18 - j]
                _color, cnt = self.count_six(stone_val, _color, cnt)

                exit_req = self.print_result(_color, cnt)
                if exit_req:
                    break

    def count_six(self, stone_val, color, cnt):
        _color = color
        _cnt = cnt
        if stone_val != _NO_STONE:
            if _color == stone_val:
                _cnt += 1
            else:
                _color = stone_val
                _cnt = 1
        else:
            _cnt = 0
        return _color, _cnt

    def print_result(self, color, cnt):
        exit_req = False
        if cnt == 6:
            result = "Black " if color == _BLACK else "White "
            print(result + "Wins!")
            exit_req = True
        elif cnt > 6:
            result = "Black " if color == _BLACK else "White "
            print(result + "Loses!")
            exit_req = True
        return exit_req


def main():

    move = 1  # N수.. 이런거 나타내주는 변수
    _TURN = -1

    while True:
        pygame.time.wait(10)  # 게임 딜레이 타임 이라고 하는게 좋을듯 ㅇㅇ
        for event in pygame.event.get():  # 사용자가 무언가를 했다.
            if event.type == pygame.QUIT:  # 사용자가 종료 버튼을 누른 경우
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # 사용자가 마우스 버튼을 누른 경우
                if event.button == 1 and board.outline.collidepoint(event.pos):
                    if _TURN == _BLACK:
                        x = int(round(((event.pos[0] - 5) / 40.0), 0))
                        y = int(round(((event.pos[1] - 5) / 40.0), 0))
                        added_stone = Stone(board, (x, y), board.turn(move))
                        board.update_stone_set(added_stone)
                        board.update_stone_order(added_stone)

                        print("______________   MOVE: " + str(move) + "   ______________")
                        print("Added Stone: " + str(added_stone))
                        board.print_stone_set()

                    board.win()
                    move += 1
                    """
                    stone = board.search(point=(x, y))
                    if stone:  # 사용자가 돌을 클릭 했을 경우
                        stone.remove()
                        move -= 1
                    else:  # 그 외인 경우
                        added_stone = Stone(board, (x, y), board.turn(move))  # added_stone은 Stone 객체다
                        print(added_stone)
                        move += 1
                    #board.update_liberties(added_stone)  # 데이터 들어가는 순서 1번
                    """

        '''여기에다가 인공지능 관련 코드를 적어야한다.'''
        if _TURN == _WHITE:
            print("counter")
            # ai = AI.AI(board)
            ai2 = AI2.AI(board)
            y, x = ai2.final_move()

            # weight = ai.half_move_evaluation_algorithm(x - 1, y - 1)

            added_stone = Stone(board, (x + 1, y + 1), board.turn(move))
            board.update_stone_set(added_stone)
            board.update_stone_order(added_stone)

            print("______________   MOVE: " + str(move) + "   ______________")
            print("Added Stone: " + str(added_stone))
            print("attack_threat: " + str(ai2.a_threat))
            print("defense_threat: " + str(ai2.d_threat))
            board.print_stone_set()
            # print("Current Weight: " + str(weight))

            move += 1
            board.win()

        '''현재 누구 턴인지 판별하는 코드'''
        if move % 4 == 0 or move % 4 == 1:
            _TURN = _BLACK
        else:
            _TURN = _WHITE


if __name__ == '__main__':
    pygame.init()  # 파이게임 모듈 초기화
    pygame.display.set_caption('Connect6')  # 캡션 달기
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)  # 스크린 크기 설
    background = pygame.image.load(BACKGROUND).convert()
    board = Board()  # 육목판 그리는 과정
    main()
