from sys import maxsize

_NO_STONE = 0
_BLACK = 1
_WHITE = 2

_AI = _WHITE
_OPPONENT = _BLACK

stone_weight = [2**12, 2**11, 2**10, 2**9, 2**8]
empty_weight = 2

DEPTH_THRESHOLD = 5  # 몇 수 앞까지 볼 것인가
EXPANSION_THRESHOLD = 4  # 몇 개의 자리를 탐색할 것인가 (높은 거 4개로 자식 노드 확장)

GAME_OVER = -1

search_state = [0 * DEPTH_THRESHOLD]

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
        E = 0
        threat = 0
        total_a_para = []
        total_b_para = []

        '''해당 자리 주변 영역을 탐색하는 코드'''

        '''1. 수평선 영역'''
        input_list = []
        for i in range(1, 6):
            if eval_x - i < 0:
                continue
            input_list.append(self.stone_set[eval_y][eval_x - i])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_x + i > 18:
                continue
            # print(eval_stone_x + i)
            input_list.append(self.stone_set[eval_y][eval_x + i])
        total_b_para.append(input_list)

        '''2. 수직선 영역'''
        input_list = []
        for i in range(1, 6):
            if eval_y - i < 0:
                continue
            input_list.append(self.stone_set[eval_y - i][eval_x])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_y + i > 18:
                continue
            input_list.append(self.stone_set[eval_y + i][eval_x])
        total_b_para.append(input_list)

        '''3. 2시 및 8시 방향 대각선 영역'''
        input_list = []
        for i in range(1, 6):
            if eval_x - i < 0 or eval_y + i > 18:
                continue
            input_list.append(self.stone_set[eval_y + i][eval_x - i])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_y - i < 0 or eval_x + i > 18:
                continue
            input_list.append(self.stone_set[eval_y - i][eval_x + i])
        total_b_para.append(input_list)

        '''4. 10시 및 4시 방향 대각선'''
        input_list = []
        for i in range(1, 6):
            if eval_x - i < 0 or eval_y - i < 0:
                continue
            input_list.append(self.stone_set[eval_y - i][eval_x - i])
        total_a_para.append(input_list)

        input_list = []
        for i in range(1, 6):
            if eval_x + i > 18 or eval_y + i > 18:
                continue
            input_list.append(self.stone_set[eval_y + i][eval_x + i])
        total_b_para.append(input_list)

        '''논문에 기반한 가중치 알고리즘 연산'''
        for j in range(4):
            E_directional = 1

            idx_cnt = 0
            for a_k in total_a_para[j]:
                if a_k == team_side and a_k != _NO_STONE: # 방어형 알고리즘이라서 선택되는 팀이 반대다.
                    break
                elif a_k == _NO_STONE:
                    E_directional *= empty_weight
                elif a_k != team_side:
                    E_directional *= stone_weight[idx_cnt]
                idx_cnt += 1

            idx_cnt = 0
            for b_k in total_b_para[j]:
                if b_k == team_side and b_k != _NO_STONE:
                    break
                elif b_k == _NO_STONE:
                    E_directional *= empty_weight
                elif b_k != team_side:
                    E_directional *= stone_weight[idx_cnt]
                idx_cnt += 1

            E += E_directional
            # E = 1

        # 그냥 아래에다가 win 함수 내용을 넣자.

        for j in range(4):
            if len(total_a_para[j]) != 0 and len(total_b_para[j]) != 0:
                if total_a_para[j][0] == team_side and total_b_para[j][0] == team_side:
                    '''해당 자리 양 옆이 자신의 편인 경우'''
                    a_cnt = 0
                    b_cnt = 0
                    for a in total_a_para[j]:
                        if a == team_side:
                            a_cnt += 1
                        else:
                            break
                    for b in total_b_para[j]:
                        if b == team_side:
                            b_cnt += 1
                        else:
                            break
                    if threat_min <= a_cnt + b_cnt <= threat_max:
                        print("MAX")
                        threat += 1
                        E = maxsize
                elif total_a_para[j][0] == team_side and total_b_para[j][0] != team_side:
                    '''해당 자리 한쪽만 자신의 편인 경우(왼쪽)'''
                    cnt = 0
                    for a in total_a_para[j]:
                        if a == team_side:
                            cnt += 1
                        else:
                            break
                    if threat_min <= cnt <= threat_max:
                        print("MAX")
                        threat += 1
                        E = maxsize
                elif total_a_para[j][0] != team_side and total_b_para[j][0] == team_side:
                    '''해당 자리 한쪽만 자신의 편인 경우(오른쪽)'''
                    cnt = 0
                    for b in total_b_para[j]:
                        if b == team_side:
                            cnt += 1
                        else:
                            break
                    if threat_min <= cnt <= threat_max:
                        print("MAX")
                        threat += 1
                        E = maxsize
            elif not(len(total_a_para[j]) == 0 and len(total_b_para[j]) == 0):
                if len(total_a_para[j]) == 0:
                    '''왼쪽이 아예 둘 곳이 없는 경우'''
                    if total_b_para[j][0] == team_side:
                        cnt = 0
                        for b in total_b_para[j]:
                            if b == team_side:
                                cnt += 1
                            else:
                                break
                        if threat_min <= cnt <= threat_max:
                            print("MAX")
                            threat += 1
                            E = maxsize

                if len(total_b_para[j]) == 0:
                    '''오른쪽이 아예 둘 곳이 없는 경우'''
                    if total_a_para[j][0] == team_side:
                        cnt = 0
                        for a in total_a_para[j]:
                            if a == team_side:
                                cnt += 1
                            else:
                                break
                        if threat_min <= cnt <= threat_max:
                            print("MAX")
                            threat += 1
                            E = maxsize

        return E, threat