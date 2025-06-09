import grpc
from concurrent import futures
import logging

import sys
sys.path.append(r'../../generated/sudoku')

import sudoku_pb2
import sudoku_pb2_grpc

N = 9

class SudokuServicer(sudoku_pb2_grpc.SudokuServiceServicer):
    def is_safe(self, board, row, col, num):
        for x in range(N):
            if board[row][x] == num or board[x][col] == num or \
               board[(row // 3) * 3 + x // 3][(col // 3) * 3 + x % 3] == num:
                return False
        return True

    def hidden_singles(self, board):
        found = False
        for num in range(1, 10):
            # Проверка боксов
            for box_row in range(3):
                for box_col in range(3):
                    start_row = box_row * 3
                    start_col = box_col * 3
                    possible_positions = []

                    for i in range(3):
                        for j in range(3):
                            row_idx = start_row + i
                            col_idx = start_col + j
                            if board[row_idx][col_idx] == 0 and self.is_safe(board, row_idx, col_idx, num):
                                possible_positions.append((row_idx, col_idx))
                    if len(possible_positions) == 1:
                        r, c = possible_positions[0]
                        board[r][c] = num
                        found = True

            # Проверка строк и столбцов
            for i in range(N):
                possible_row_pos = -1
                for j in range(N):
                    if board[i][j] == 0 and self.is_safe(board, i, j, num):
                        if possible_row_pos == -1:
                            possible_row_pos = j
                        else:
                            possible_row_pos = -2
                            break
                if possible_row_pos >= 0:
                    board[i][possible_row_pos] = num
                    found = True

                possible_col_pos = -1
                for j in range(N):
                    if board[j][i] == 0 and self.is_safe(board, j, i, num):
                        if possible_col_pos == -1:
                            possible_col_pos = j
                        else:
                            possible_col_pos = -2
                            break
                if possible_col_pos >= 0:
                    board[possible_col_pos][i] = num
                    found = True

        return found

    def backtrack_solve(self, board, steps=None, is_steps=False):
        for row in range(N):
            for col in range(N):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_safe(board, row, col, num):
                            board[row][col] = num
                            if is_steps and steps is not None:
                                self.save_step(board, steps)
                            if self.backtrack_solve(board, steps, is_steps):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def save_step(self, current_board, steps_list):
        # Создаем копию доски и добавляем в список шагов
        step_copy = [row[:] for row in current_board]
        steps_list.append(step_copy)

    def parse_board_from_string(self, s):
        if len(s) != N * N:
            raise ValueError(f"Длина строки должна быть {N*N}")
        board = []
        for i in range(N):
            row_vals = []
            for j in range(N):
                ch = s[i * N + j]
                if not ch.isdigit():
                    raise ValueError(f"Недопустимый символ: {ch}")
                row_vals.append(int(ch))
            board.append(row_vals)
        return board

    def solve_sudoku(self, initial_board_str, is_steps_flag):
        try:
            board = self.parse_board_from_string(initial_board_str)
        except ValueError as e:
            raise e

        steps_list = []

        strategy_applied = True

        while strategy_applied:
            strategy_applied = False
            if self.hidden_singles(board):
                strategy_applied = True
                if is_steps_flag:
                    self.save_step(board, steps_list)

            # Можно добавить другие стратегии по мере необходимости...

        success = self.backtrack_solve(board, steps_list if is_steps_flag else None, is_steps_flag)
        if not success:
            raise RuntimeError("Не удалось решить судоку")

        solution_str = self.board_to_string(board)
        steps_str = self.steps_to_string(steps_list)

        return solution_str, steps_str

    def board_to_string(self, board):
        return ''.join(str(cell) for row in board for cell in row)

    def steps_to_string(self, steps):
        result_chars = []
        for step in steps:
            result_chars.extend(str(cell) for row in step for cell in row)
        return ''.join(result_chars)

    def Solve(self, request: sudoku_pb2.SudokuRequest,
              context) -> sudoku_pb2.SudokuResponse:
        initial_board_str = request.puzzle
        is_steps_flag = request.isSteps

        try:
            solution_str, steps_str = self.solve_sudoku(initial_board_str, is_steps_flag)
            if is_steps_flag:
                return sudoku_pb2.SudokuResponse(solution=steps_str)
            else:
                return sudoku_pb2.SudokuResponse(solution=solution_str)
        except Exception as e:
            return sudoku_pb2.SudokuResponse(solution="", error=e)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SudokuServiceServicer_to_server(SudokuServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Sudoku сервис слушает на :50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()