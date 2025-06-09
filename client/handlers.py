import json
import grpc
import logging
from flask import Flask, request, jsonify

import sys
sys.path.append(r'../generated/auth')
sys.path.append(r'../generated/sudoku')

import auth_pb2
import auth_pb2_grpc
import sudoku_pb2
import sudoku_pb2_grpc

app = Flask(__name__)

# Создаем gRPC клиентов
auth_channel = grpc.insecure_channel('localhost:50052')
auth_client = auth_pb2_grpc.AuthServiceStub(auth_channel)

sudoku_channel = grpc.insecure_channel('localhost:50051')
sudoku_client = sudoku_pb2_grpc.SudokuServiceStub(sudoku_channel)

# Обработчики HTTP-запросов

@app.route('/api/register', methods=['POST'])
def handle_register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    try:
        ctx = grpc.aio or grpc
        response = auth_client.Register(auth_pb2.RegisterRequest(
            username=username,
            password=password
        ), timeout=5)
        return jsonify({'success': response.success})
    except Exception as e:
        print("Auth Register error:", e)
        return jsonify({'success': False, 'message': 'Auth service error'}), 500

@app.route('/api/login', methods=['POST'])
def handle_login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
    except Exception:
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
        print("Auth Login error:", e)
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/api/solve', methods=['POST'])
def handle_solve():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        puzzle = data['Puzzle']
        isSteps = data['IsSteps']
    except Exception:
        return jsonify({'error': 'Invalid request'}), 400

    try:
        response = sudoku_client.Solve(sudoku_pb2.SudokuRequest(
            puzzle=puzzle,
            isSteps=isSteps
        ), timeout=5)
        return jsonify({'solution': response.solution})
    except Exception as e:
        print("Sudoku solve error:", e)
        return jsonify({'error': "Данное судоку не имеет решения"}), 200

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

if __name__ == '__main__':
    # Настройка статической папки
    app.static_folder = './static'
    print("Server started at :8080")
    app.run(host='0.0.0.0', port=8080)