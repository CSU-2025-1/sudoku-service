import json
import grpc
import logging
from flask import Flask, request, jsonify

import sys

from jwt_token.jwt_check import check_token_valid

sys.path.append(r'../generated/auth')
sys.path.append(r'../generated/sudoku')

import auth_pb2
import auth_pb2_grpc
import sudoku_pb2
import sudoku_pb2_grpc

app = Flask(__name__)

# Создаем gRPC клиентов
auth_channel = grpc.insecure_channel('auth:50052')
auth_client = auth_pb2_grpc.AuthServiceStub(auth_channel)

sudoku_channel = grpc.insecure_channel('solver:50051')
sudoku_client = sudoku_pb2_grpc.SudokuServiceStub(sudoku_channel)


# Обработчики HTTP-запросов
@app.route('/api/register', methods=['POST'])
def handle_register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
    except Exception as e:
        logging.fatal(f"Invalid request error: {e}")
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    try:
        ctx = grpc.aio or grpc
        response = auth_client.Register(auth_pb2.RegisterRequest(
            username=username,
            password=password
        ), timeout=5)
        return jsonify({'success': response.success})
    except Exception as e:
        logging.fatal(f"Auth Register error: {e}")
        return jsonify({'success': False, 'message': 'Auth service error'}), 500


@app.route('/api/login', methods=['POST'])
def handle_login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
    except Exception as e:
        logging.fatal(f"Invalid request error: {e}")
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    try:
        response = auth_client.Login(auth_pb2.LoginRequest(
            username=username,
            password=password
        ), timeout=5)
        return jsonify({
            'success': response.success,
            'token': response.token,
            'message': ''
        })
    except Exception as e:
        logging.fatal(f"Auth Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500


@app.route('/api/solve', methods=['POST'])
def handle_solve():
    token = request.headers.get('Authorization')
    check_result = check_token_valid(token)
    if check_result:
        return check_result
    try:
        data = request.get_json()
        puzzle = data['Puzzle']
        is_steps = data['IsSteps']
    except Exception as e:
        logging.fatal(f"Invalid request error: {e}")
        return jsonify({'error': 'Invalid request'}), 400

    try:
        response = sudoku_client.Solve(sudoku_pb2.SudokuRequest(
            puzzle=puzzle,
            isSteps=is_steps
        ), timeout=5)
        return jsonify({'solution': response.solution})
    except Exception as e:
        logging.fatal(f"Sudoku solve error: {e}")
        return jsonify({'error': "Данное судоку не имеет решения"}), 200


@app.route('/api/sudoku', methods=['GET'])
def get_sudokus():
    token = request.headers.get('Authorization')
    check_result = check_token_valid(token)
    if check_result:
        return check_result

    try:
        response = sudoku_client.GetSudokuList(sudoku_pb2.GetSudokuRequest(token=token), timeout=5)

        sudoku_data = {
            'ids': list(response.ids),
            'boards': list(response.boards),
            'difficulties': list(response.difficulties),
            'is_solved': list(response.isSolved)
        }

        return jsonify(sudoku_data)
    except Exception as e:
        logging.fatal(f'Sudoku get error: {e}')
        return jsonify({'error': 'Не удалось получить судоку'}), 500


@app.route('/api/check_sudoku', methods=['POST'])
def check_sudoku():
    token = request.headers.get('Authorization')
    check_result = check_token_valid(token)
    if check_result:
        return check_result
    try:
        data = request.get_json()
        solution = data['Solution']
        sudoku_id = data['SudokuId']
    except Exception as e:
        logging.fatal(f"Invalid request error: {e}")
        return jsonify({'error': 'Invalid request'}), 400

    try:
        response = sudoku_client.CheckSudoku(sudoku_pb2.CheckSudokuRequest(solution=solution,
                                                                           token=token,
                                                                           sudokuId=sudoku_id), timeout=5)
        return jsonify({'isCorrect': response.isCorrect})
    except Exception as e:
        logging.fatal(f'Sudoku check error: {e}')
        return jsonify({'error': 'Не удалось проверить решение'}), 500


# Статические файлы (HTML)
@app.route('/register.html')
def serve_register_page():
    return app.send_static_file('register.html')


@app.route('/login.html')
def serve_login_page():
    return app.send_static_file('login.html')


@app.route('/sudoku.html')
def serve_sudoku_page():
    return app.send_static_file('sudoku.html')


@app.route('/play_sudoku.html')
def serve_play_sudoku_page():
    return app.send_static_file('play_sudoku.html')


if __name__ == '__main__':
    # Настройка статической папки
    app.static_folder = './static'
    print("Server started at :8080")
    app.run(host='0.0.0.0', port=8080)
