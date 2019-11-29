import numpy as np
import random

import loggers as lg

from games.connect6.game import Game, GameState
# from game import Game, GameState
from model import Residual_CNN

from agent import Agent, User

import config


# 그냥 플레이어 객체 초기화 시켜주는 코드다
def playMatchesBetweenVersions(env, run_version, player1version, player2version, EPISODES, logger, turns_until_tau0, goes_first=0):
    # turns_until_tau0: logger 관련 값 ->

    # player1 객체 초기화
    if player1version == -1:  # 인간일 경우
        player1 = User('player1', env.state_size, env.action_size)
    else:
        player1_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)

        if player1version > 0:
            player1_network = player1_NN.read(env.name, run_version, player1version)
            player1_NN.model.set_weights(player1_network.get_weights())   
        player1 = Agent('player1', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player1_NN)

    # player2 객체 초기화
    if player2version == -1:  # 인간일 경우
        player2 = User('player2', env.state_size, env.action_size)
    else:
        player2_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape, env.action_size, config.HIDDEN_CNN_LAYERS)
        
        if player2version > 0:
            player2_network = player2_NN.read(env.name, run_version, player2version)
            player2_NN.model.set_weights(player2_network.get_weights())
        player2 = Agent('player2', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player2_NN)

    # 아래 코드가 핵심이다.
    scores, memory, points, sp_scores = playMatches(player1, player2, EPISODES, logger, turns_until_tau0, None, goes_first)
    return scores, memory, points, sp_scores


# 실제 경기 시뮬레이션 돌리는 코드 (인공지능 활성화가 아닌 경기 생성)
def playMatches(player1, player2, EPISODES, logger, turns_until_tau0, memory=None, goes_first=0):
    # turns_until_tau0: logger 관련 값 ->

    env = Game()
    scores = {player1.name: 0, "drawn": 0, player2.name: 0}
    sp_scores = {'sp': 0, "drawn": 0, 'nsp': 0}
    points = {player1.name: [], player2.name: []}

    for e in range(EPISODES):  # 진행하는 게임 횟수

        logger.info('====================')
        logger.info('EPISODE %d OF %d', e+1, EPISODES)
        logger.info('====================')

        print(str(e + 1) + ' ', end='')

        state = env.reset()  # 게임 초기화
        
        done = 0
        turn = 0
        player1.mcts = None
        player2.mcts = None

        '''누가 먼저 하실?? ㅇㅇ 이거 정하는 코드 및 정해지면 그와 관련 된 로그 저장'''
        if goes_first == 0:  # 이게 0이면 시작 순서 랜덤으로 하겠다~ 이 소리
            player1Starts = random.randint(0, 1) * 2 - 1
        else:
            player1Starts = goes_first

        if player1Starts == 1:  # player1이 먼저 시작
            players = {1: {"agent": player1, "name": player1.name}
                    , -1: {"agent": player2, "name": player2.name}
                    }
            logger.info(player1.name + ' plays as X')
        else:   # player2가 먼저 시작
            players = {1: {"agent": player2, "name": player2.name}
                    , -1: {"agent": player1, "name": player1.name}
                    }
            logger.info(player2.name + ' plays as X')
            logger.info('--------------')

        env.gameState.render(logger)  # 그냥 보드판 새로 그려줌.

        ''''''
        while done == 0:  # 경기가 끝나지 않은 경우
            turn = turn + 1  # 계속 n수씩 증가
            print(turn)
            state.playerTurn = 1 if turn % 4 == 0 or turn % 4 == 1 else -1  # 육목의 특성 상, 이 코드를 추가해야한다.

            #### Run the MCTS algo and return an action
            # 인공지능이 결정한 action 출력하는 코드
            if turn < turns_until_tau0:  # turn on which it starts playing deterministically
                action, pi, MCTS_value, NN_value = players[state.playerTurn]['agent'].act(state, 1)
            else:
                action, pi, MCTS_value, NN_value = players[state.playerTurn]['agent'].act(state, 0)

            print('action: %d', action)
            if memory != None:
                ####Commit the move to memory
                memory.commit_stmemory(env.identities, state, pi)

            logger.info('action: %d', action)
            '''
            for r in range(env.grid_shape[0]):
                logger.info(['----' if x == 0 else '{0:.2f}'.format(np.round(x,2)) for x in pi[env.grid_shape[1]*r : (env.grid_shape[1]*r + env.grid_shape[1])]])
            logger.info('MCTS perceived value for %s: %f', state.pieces[str(state.playerTurn)] ,np.round(MCTS_value,2))
            logger.info('NN perceived value for %s: %f', state.pieces[str(state.playerTurn)] ,np.round(NN_value,2))
            logger.info('====================')
            '''
            
            ### Do the action
            state, value, done, _ = env.step(action)    # the value of the newState from the POV of the new playerTurn i.e. -1 if the previous player played a winning move
            env.gameState.render(logger)    # 사용자가 볼 수 있게 로그창에 인공지능이 착수한 로그 생성
            if done == 1:  # 경기가 종료된 경우
                if memory != None:  # 메모리 관련 코드인데 저도 잘...
                    #### If the game is finished, assign the values correctly to the game moves
                    for move in memory.stmemory:
                        if move['playerTurn'] == state.playerTurn:
                            move['value'] = value
                        else:
                            move['value'] = -value
                         
                    memory.commit_ltmemory()
             
                if value == 1:  # 깃허브에서 제기한 오류 문제. 얘는 절대 1이 될 수 없다.
                    logger.info('%s WINS!', players[state.playerTurn]['name'])
                    scores[players[state.playerTurn]['name']] = scores[players[state.playerTurn]['name']] + 1
                    if state.playerTurn == 1: 
                        sp_scores['sp'] = sp_scores['sp'] + 1
                    else:
                        sp_scores['nsp'] = sp_scores['nsp'] + 1

                elif value == -1:
                    logger.info('%s WINS!', players[-state.playerTurn]['name'])
                    scores[players[-state.playerTurn]['name']] = scores[players[-state.playerTurn]['name']] + 1
               
                    if state.playerTurn == 1: 
                        sp_scores['nsp'] = sp_scores['nsp'] + 1
                    else:
                        sp_scores['sp'] = sp_scores['sp'] + 1

                else:
                    logger.info('DRAW...')
                    scores['drawn'] = scores['drawn'] + 1
                    sp_scores['drawn'] = sp_scores['drawn'] + 1

                pts = state.score
                points[players[state.playerTurn]['name']].append(pts[0])
                points[players[-state.playerTurn]['name']].append(pts[1])

    return scores, memory, points, sp_scores
