import json
import grpc
import logging
from flask import Flask, request, jsonify

import sys

from client.jwt_token.jwt_check import is_token_valid

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
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    if not is_token_valid(token):
        return jsonify({'error': 'Token is expired'}), 401

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
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    if not is_token_valid(token):
        return jsonify({'error': 'Token is expired'}), 401

    try:
        response = sudoku_client.GetSudokuList(sudoku_pb2.SudokuRequest(
            token=token
        ), timeout=5)
        return jsonify({'ids': response.ids,
                        'boards': response.boards,
                        'difficulties': response.difficulties,
                        'is_solved': response.isSolved})
    except Exception as e:
        logging.fatal(f"Sudoku get error: {e}")
        return jsonify({'error': "Не удалось получить судоку"}), 500


@app.route('/api/sudoku/<int:sudoku_id>', methods=['GET'])
def get_sudoku(sudoku_id):
    # Возвращаем конкретный судоку с полем puzzle
    for s in sudokus:
        if s['id']==sudoku_id:
            return jsonify(s)
    return jsonify({"error":"Не найдено"}),404


@app.route('/api/check_sudoku', methods=['POST'])
def check_sudoku():
    data=request.get_json()
    sudoku_id= data.get('id')
    solution= data.get('solution') # массив из чисел

    if sudoku_id is None or solution is None:
        return jsonify({"correct":False}),400

    # На заглушке просто считаем верным если сумма чисел равна определенному значению или по условию.
    # Или делаем простую проверку — например все числа от 1 до 9 без нулей.
    correct=True
    for num in solution:
        if num<1 or num>9:
            correct=False
            break

    # Можно дополнительно проверить соответствие исходной головоломке и т.п.

    # Обновляем статус решения в данных (если нужно)
    for s in sudokus:
        if s['id']==sudoku_id:
            if correct:
                s['solved']=True
                break

    return jsonify({"correct":correct})


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
