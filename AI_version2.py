from sys import maxsize

_OUT_OF_AREA = -1
_NO_STONE = 0
_BLACK = 1
_WHITE = 2

_AI = _WHITE
_OPPONENT = _BLACK

stone_weight = [2**12, 2**11, 2**10, 2**9, 2**8]
empty_weight = 2
out_area_weight = 1

DEPTH_THRESHOLD = 5  # 몇 수 앞까지 볼 것인가
EXPANSION_THRESHOLD = 4  # 몇 개의 자리를 탐색할 것인가 (높은 거 4개로 자식 노드 확장)

GAME_OVER = -1

search_state = [0 * DEPTH_THRESHOLD]

class MinMax_Node(object):
    def __init__(self, stone_set, depth, move_cnt):
        self.stone_set = stone_set
        self.depth = depth
        self.value = 0
        self.a_threat = 0    # 다음 사용자가 놓으면 이기는 형세거나, 내가 현재 수에서 놓으면 이기는 형세
        self.d_threat = 0
        self.move_cnt = move_cnt
        self.children = []
        self.create_children(self.stone_set)
        self.team_side = _WHITE

    def create_children(self, _stone_set):
        self.move_cnt += 1
        curr_side = self.find_turn()
        ai = AI(_stone_set)

        '''높은 점수대로 착수하는 과정'''
        if self.value != GAME_OVER:
            max_tmp = maxsize
            for i in range(EXPANSION_THRESHOLD):
                attack_weight, attack_threat, attack_y, attack_x = ai.offensive_play(max_tmp, curr_side, 4, 5)
                defense_weight, defense_threat, defense_y, defense_x = ai.defensive_play(max_tmp, curr_side, 4, 5)

                if attack_weight > defense_weight:
                    _stone_set[attack_y][attack_x] = curr_side
                    max_tmp = attack_weight
                else:
                    _stone_set[defense_y][defense_x] = curr_side
                    max_tmp = defense_weight

                '''말단 노드까지 온 경우, 해당 바둑판 상황을 판단해야함.'''
                if attack_threat >= 3 or defense_threat >= 3:   # 경기가 사실상 끝난 경우
                    self.a_threat = attack_threat
                    self.d_threat = defense_threat
                    self.value = GAME_OVER
                else:
                    self.children.append(MinMax_Node(_stone_set, self.depth - 1, curr_side))
        else:
            pass

    '''말단 노드까지 오고, 착수까지 완료된 경우, 해당 바둑판 상황을 판단해야함.(민맥스 함수에서 돌리면 됨)'''
    def getNodeState(self):
        ai = AI(self.stone_set)
        attack_weight, attack_threat, attack_y, attack_x = ai.offensive_play(maxsize, self.team_side, 4, 5)
        defense_weight, defense_threat, defense_y, defense_x = ai.defensive_play(maxsize, self.team_side, 4, 5)

    def find_turn(self):
        if self.move_cnt % 4 == 0 or self.move_cnt % 4 == 1:
            return _BLACK
        else:
            return _WHITE

class AI(object):
    def __init__(self, board):
        self.board = board
        self.stone_set = self.board.stone_set
        self.black_stone_order = self.board.black_stone_order
        self.white_stone_order = self.board.white_stone_order
        self.a_threat = 0  # 디버깅을 위한 임시 변수
        self.d_threat = 0
        # self.threat = 0  # 변수 초기화는 필요없다. 어차피 ai 객체는 매 턴마다 새로 선언된다.
        # self.team_side = team_side  # 사실 근데 이건 만들어놓고 안쓰고 있다.

    '''첫 수는 검은 돌이 하나를 놓는데, 이에 대한 조건 연산은 아직 구현 X'''
    '''검은 돌이 제일 유리한 포지션을 없애는 것이 아래 알고리즘 목표다'''

    def final_move(self):
        attack_weight, self.a_threat, attack_y, attack_x = self.offensive_play(maxsize, _AI, 4, 5)
        defense_weight, self.d_threat, defense_y, defense_x = self.defensive_play(maxsize, _AI, 4, 5)

        if attack_weight > defense_weight:
            return [attack_y, attack_x]
        else:
            return [defense_y, defense_x]

    '''MinMax 탐색 기법 사용'''
    def MinMax(self, node, depth):
        if depth == 0 or node.a_threat >= 2 or node.d_threat >= 2:
            return node.value

        best_value = -1
        for i in range(EXPANSION_THRESHOLD):
            child = node.children[i]
            value = self.MinMax(child, depth - 1)

            if i == 0:
                best_value = value
            else:
                if node.team_side == _AI:
                    best_value = max(best_value, value)
                else:
                    best_value = min(best_value, value)

        return best_value

    def MiniMax(self, node, depth, maximizingPlayer):
        if depth == 0 or node.value == GAME_OVER:
            return 100

        if maximizingPlayer:
            value = -maxsize
            for child in node.children:
                value = max(value, self.MiniMax(child, depth - 1, False))
            return value
        else:
            value = maxsize
            for child in node.children:
                value = min(value, self.MiniMax(child, depth - 1, True))
            return value

    def offensive_play(self, max_limit, user, threat_min, threat_max):
        max_weight = -1
        result = []
        ay, by = self.roi_y()
        ax, bx = self.roi_x()
        calculated_w = -1
        calculated_th = -1
        for y in range(ay, by + 1):
            for x in range(ax, bx + 1):
                if self.stone_set[y][x] == _NO_STONE:
                    if user == _AI:
                        calculated_w, calculated_th = self.half_move_evaluation_algorithm(x, y, _OPPONENT, threat_min, threat_max)
                    elif user == _OPPONENT:
                        calculated_w, calculated_th = self.half_move_evaluation_algorithm(x, y, _AI, threat_min, threat_max)

                    if max_weight < calculated_w <= max_limit:
                        max_weight = calculated_w
                        result = [max_weight, calculated_th, y, x]
        return result

    def defensive_play(self, max_limit, user, threat_min, threat_max):
        max_weight = -1
        result = []
        ay, by = self.roi_y()
        ax, bx = self.roi_x()
        for y in range(ay, by + 1):
            for x in range(ax, bx + 1):
                if self.stone_set[y][x] == _NO_STONE:
                    calculated_w, calculated_th = self.half_move_evaluation_algorithm(x, y, user, threat_min, threat_max)
                    if max_weight < calculated_w <= max_limit:
                        max_weight = calculated_w
                        result = [max_weight, calculated_th, y, x]
        return result

    def roi_y(self):
        ay = 100  # 100 -> null의 역할
        by = -100  # -100 -> null의 역할

        for x in range(19):
            for y in range(18, -1, -1):
                if self.stone_set[y][x] != _NO_STONE and y < ay:
                    ay = y
                    break
        for x in range(19):
            for y in range(18, -1, -1):
                if self.stone_set[y][x] != _NO_STONE and y > by:
                    by = y
                    break

        if ay >= 2:
            ay -= 2
        else:
            ay = 0
        if by <= 16:
            by += 2
        else:
            by = 18

        return ay, by

    def roi_x(self):
        ax = 100    # 100 -> null의 역할
        bx = -100   # -100 -> null의 역할

        for y in range(19):
            for x in range(19):
                if self.stone_set[y][x] != _NO_STONE and x < ax:
                    ax = x
                    break
        for y in range(19):
            for x in range(18, -1, -1):
                if self.stone_set[y][x] != _NO_STONE and x > bx:
                    bx = x
                    break

        if ax >= 2:
            ax -= 2
        else:
            ax = 0
        if bx <= 16:
            bx += 2
        else:
            bx = 18

        return ax, bx

    '''현재 팀이 흰 돌, 상대팀이 검은 돌이라 가정한다.'''
    def find_recent_move(self):
        recent_move = [-1, -1, -1, -1]

        for y in range(19):
            for x in range(19):
                if self.board.black_cnt - 1 == self.board.black_stone_order[y][x]:
                    recent_move[0] = y
                    recent_move[1] = x

                if self.board.black_cnt == self.board.black_stone_order[y][x]:
                    recent_move[2] = y
                    recent_move[3] = x

        '''같은 연산이 두번 반복 된다. 뭐 알아서 조심하셈 ㅇㅇㅇ(버그 날 확률 매우 높아!!!)'''
        if recent_move[0] == -1:    # 첫 수인 경우
            recent_move[0] = recent_move[2]
            recent_move[1] = recent_move[3]
            recent_move[2] = -1
            recent_move[3] = -1

        return recent_move

    '''게임 상황에 대한 유불리함 가중치 둬주는 알고리즘 - 방어형 알고리즘이다.'''
    def half_move_evaluation_algorithm(self, eval_x, eval_y, team_side, threat_min, threat_max):
        weight = 0
        threat = 0
        total_a_para = []
        total_b_para = []

        '''해당 자리 주변 영역을 탐색하는 코드'''

        '''1. 수평선 영역'''
        input_list = []
        for i in range(1, 6):
            if eval_x - i < 0:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y][eval_x - i])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_x + i > 18:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y][eval_x + i])
        total_b_para.append(input_list)

        '''2. 수직선 영역'''
        input_list = []
        for i in range(1, 6):
            if eval_y - i < 0:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y - i][eval_x])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_y + i > 18:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y + i][eval_x])
        total_b_para.append(input_list)

        '''3. 2시 및 8시 방향 대각선 영역'''
        input_list = []
        for i in range(1, 6):
            if eval_x - i < 0 or eval_y + i > 18:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y + i][eval_x - i])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_y - i < 0 or eval_x + i > 18:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y - i][eval_x + i])
        total_b_para.append(input_list)

        '''4. 10시 및 4시 방향 대각선'''
        input_list = []
        for i in range(1, 6):
            if eval_x - i < 0 or eval_y - i < 0:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y - i][eval_x - i])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_x + i > 18 or eval_y + i > 18:
                input_list.append(_OUT_OF_AREA)
            else:
                input_list.append(self.stone_set[eval_y + i][eval_x + i])
        total_b_para.append(input_list)

        '''논문에 기반한 가중치 알고리즘 연산'''
        for j in range(4):
            weight_directional = 1

            idx_cnt = 0
            for a_k in total_a_para[j]:
                if a_k != team_side or a_k == _OUT_OF_AREA:
                    break
                elif a_k == _NO_STONE:
                    weight_directional *= empty_weight
                elif a_k == team_side:
                    weight_directional *= stone_weight[idx_cnt]
                idx_cnt += 1

            idx_cnt = 0
            for b_k in total_b_para[j]:
                if b_k != team_side or b_k == _OUT_OF_AREA:
                    break
                elif b_k == _NO_STONE:
                    weight_directional *= empty_weight
                elif b_k == team_side:
                    weight_directional *= stone_weight[idx_cnt]
                idx_cnt += 1

            weight += weight_directional
        return weight, threat