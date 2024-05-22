# pipe.py: Implementacao do projeto de Inteligencia Artificial 2023/2024.

# Grupo 45:
# 106064 Miguel Casimiro Barbosa
# 107095 David Costa Quintino

import sys

import copy
import numpy as np
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

convert_piece = {"FC": "1000", "FB": "0010", "FE": "0001", "FD": "0100",
                  "BC": "1101", "BB": "0111", "BE": "1011", "BD": "1110",
                  "VC": "1001", "VB": "0110", "VE": "0011", "VD": "1100",
                  "LH": "0101", "LV": "1010"}


convert_piece_F = ["1000", "0100", "0010", "0001"]
convert_piece_B = ["1101", "1110", "0111", "1011"]
convert_piece_V = ["1001", "1100", "0110", "0011"]
convert_piece_L = ["0101", "1010"]


class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representacao interna de um tabuleiro de PipeMania."""
    def __init__(self, grid):
        self.grid = grid
        self.size = len(grid) 


    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posicao do tabuleiro e
        se a peca foi vista"""
        return self.grid[row][col]
    

    def get_piece(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posicao do tabuleiro"""
        return self.grid[row][col][0:2]
    

    def set_value(self,row: int, col: int, value: str):
        self.grid[row][col] = value


    def rotate_piece(self,row: int, col: int, rotation: str):
        #C B E D, H V
        newpiece = self.get_value(row,col)[0] + rotation + '1'
        self.grid[row][col] = newpiece
        return
    

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str): # type: ignore
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        above_value = self.get_value(row-1,col) if row > 0 else None
        below_value = self.get_value(row+1,col) if row < self.size - 1 else None
        return above_value,below_value


    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str): # type: ignore
        """Devolve os valores imediatamente a esquerda e a direita,
        respectivamente."""
        self.get_value(row,col)
        left_value = self.get_value(row, col-1) if col > 0 else None
        right_value = self.get_value(row, col+1) if col < self.size - 1 else None
        return left_value,right_value


    def get_adjacent_values(self, row: int, col: int):
        
        (cima,baixo) = self.adjacent_vertical_values(row,col)
        (esquerda,direita) = self.adjacent_horizontal_values(row,col)
        return (cima,direita,baixo,esquerda)


    def print_grid(self):
        # TODO
        
        for i in range(self.size):
            aux = "" 
            for j in range(self.size):
                if(j == self.size - 1):
                    aux = aux + self.get_value(i, j)[:2]
                else:
                    aux = aux + self.get_value(i, j)[:2] + "\t"
            print(aux)
        return
    
    

    
    def piece_corrected(self, row: int,  col: int): 
        return self.get_value(row,col)[2] == '1'


    def connections(self, row: int, col: int):
        
        vizinho_cima,vizinho_direita,vizinho_baixo,vizinho_esquerda = self.get_adjacent_values(row,col)
        vizinhos = (vizinho_cima,vizinho_direita,vizinho_baixo,vizinho_esquerda)
        res = [2,2,2,2] # inicializar como desconhecido
        num_ones = 0
        piece = self.get_piece(row,col) #ver o caso de duas fontes uma contra a outra
        for i in range(4):
            if (vizinhos[i] == None) or (piece[0] == 'F' and vizinhos[i][0] == 'F'): res[i] = 0 #ve se o vizinho e none
            elif vizinhos[i][2] == '0' : res[i] = 2 # ve se ainda nao foi tratado
            elif convert_piece[vizinhos[i][0:2]][(i + 2) % 4] == '1': #converte para bits e ve se o vizinho aponta para a peca
                    res [i] = 1 
                    num_ones +=1
            else: res[i] = 0 #senao nao aponta
        return (res, num_ones)


    def comparisons(self, row: int, col: int):

        piece = self.get_value(row, col)
        connections, num_ones = self.connections(row, col)
        '''
        No connections, devolve um array de len = 4 com o seguinte formato:
            -> Se for 0, ou o adjacente e None ou foi visto e nao aponta
                - CASO ESPECIFICO: Se estivermos a tratar uma peca que seja um 
                'F', retorna 0 se o adjacente tambem o for
            -> Se for 1, o adjacente ja foi visto e aponta para a peca
            -> Se for 2, o adjacente ja foi visto, mas nao aponta para a peca
        '''
        rotations = []
        possible_piece = True
        keys = ['C','D','B','E']
        keys_L = ['H', 'V']

        j = 0
        if(piece[0] == 'F'):
            if(num_ones > 1):
                return rotations
            for binary_piece in convert_piece_F:
                possible_piece = True
                for i in range(4):
                    if (binary_piece[i] == '1' and connections[i] == 0) or (binary_piece[i] == '0' and connections[i] == 1):
                        possible_piece = False
                        break
                
                if possible_piece:
                    rotations.append('F' + keys[j] + '1')
                j+= 1

            return rotations

        elif(piece[0] == 'B'):
            if(num_ones > 3):
                return rotations
            for binary_piece in convert_piece_B:
                possible_piece = True
                
                for i in range(4):
                    if (binary_piece[i] == '1' and connections[i] == 0) or (binary_piece[i] == '0' and connections[i] == 1):
                        possible_piece = False
                        break
                
                if possible_piece:
                    rotations.append('B' + keys[j] + '1')
                j+= 1

            return rotations


        elif(piece[0] == 'V'):
            if(num_ones > 2):
                return rotations
            for binary_piece in convert_piece_V:
                possible_piece = True
                for i in range(4):
                    if (binary_piece[i] == '1' and connections[i] == 0) or (binary_piece[i] == '0' and connections[i] == 1):
                        possible_piece = False
                        break
                
                if possible_piece:
                    rotations.append('V' + keys[j] + '1')
                j+= 1
            return rotations

        else:   # e ligacao (L)
            if(num_ones > 2):
                return rotations
            for binary_piece in convert_piece_L:
                possible_piece = True
                for i in range(4):
                    if (binary_piece[i] == '1' and connections[i] == 0) or (binary_piece[i] == '0' and connections[i] == 1):
                        possible_piece = False
                        break
                
                if possible_piece:
                    
                    rotations.append('L' + keys_L[j] + '1')
                j+=1

            return rotations
    
    def pre_process(self):
        """
        Faz as operacoes iniciais no board
        """
        size = self.size
        altered = False
        for row in range(size):
            for col in range(size):
                piece_value = self.get_value(row, col)
                if(piece_value[2] == '1'):
                    continue                
                rotations = self.comparisons(row, col)
                if len(rotations) == 1:
                    altered = True
                    self.set_value(row, col, rotations[0])
        return altered
    
    @staticmethod
    def parse_instance():
        """
        Le o test do standard input (stdin) que e passado como argumento
        e retorna uma instancia da classe Board.
        """
        rows = []
        line = input()
        rows.append(np.array([i + '0' for i in line.split()]))
        for i in range(len(line.split()) - 1):
            line = input()
            rows.append(np.array([i + '0' for i in line.split()]))
        
        grid = np.array(rows)
        board = Board(grid)
        while(board.pre_process()):
            continue

        return board

    
        

        


class PipeMania(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.board = board
        self.goal = self.board.size


    def actions(self, state: PipeManiaState):
        """Retorna uma lista de acoes que podem ser executadas a
        partir do estado passado como argumento."""
        """
        actions = []
        best_action = 0
        best_action_
        size = state.board.size
        for row in range(size):
            for col in range(size):
        """
        
                
                
                
                    
                

                
                

    def result(self, state: PipeManiaState, action) -> PipeManiaState:
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A acao a executar deve ser uma
        das presentes na lista obtida pela execucao de
        self.actions(state)."""
        # TODO
        #action(row,col, orientation )
        #newstate = PipeManiaState(state.board) # prolly n copia ptt depois fzr copia a serio
        #newstate.board.rotate_piece(action[0],action[1],action[2])

        #return(newstate)

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e so se o estado passado como argumento e
        um estado objetivo. Deve verificar se todas as posicoes do tabuleiro
        estao preenchidas de acordo com as regras do problema."""        

        pieces_seen_count = 0
        board_grid = state.board.grid, board_size = state.board.size
        seen_pieces = set()
        stack_pieces = []
        stack_pieces.append((0, 0))
        while stack_pieces:
            current_piece = stack_pieces.pop()
            if current_piece in seen_pieces:
                continue
            else:
                pieces_seen_count +=1
                seen_pieces.add((current_piece[0], current_piece[1]))
                piece_value = state.board.get_piece(current_piece[0], current_piece[1])
                pieces_adjacent = state.board.get_adjacent_values() #definir C D B E, isto tem os valores

                for i in range(4):
                    if convert_piece[piece_value][i] == 1:
                        #falta colocar para verificar os Nones, porque caso seja um None,
                        #nao e preciso comparar com nada
                        if (i == 0 and pieces_adjacent[0] != None and \
                            convert_piece[pieces_adjacent[0]][2] == 1):

                            stack_pieces.append((current_piece[0]+1, current_piece[1]))

                        
                        elif i == 1 and pieces_adjacent[i] != None and \
                            convert_piece[pieces_adjacent[i]][3] == 1:

                            stack_pieces.append((current_piece[0], current_piece[1]+1))


                        elif i == 2 and pieces_adjacent[i] != None and \
                            convert_piece[pieces_adjacent[i]][0] == 1:

                            stack_pieces.append((current_piece[0]-1, current_piece[1]))


                        elif i == 3 and pieces_adjacent[i] != None and \
                            convert_piece[pieces_adjacent[i]][1] == 1:

                            stack_pieces.append((current_piece[0], current_piece[1]-1))
                        

                        else:
                            return False
                        

                    else:
                        continue

                    


        if(pieces_seen_count < self.goal):
            return False
        return True

    def h(self, node: Node):
        """Funcao heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:


    board = Board.parse_instance()
    
    problem = PipeMania(board)
    state = PipeManiaState(board)
    #s0.board.print_grid()

    while(state.board.pre_process()):
        continue
    state.board.print_grid()

    # Ler o ficheiro do standard input,
    # Usar uma tecnica de procura para resolver a instancia,
    # Retirar a solucao a partir do no resultante,
    # Imprimir para o standard output no formato indicado.
