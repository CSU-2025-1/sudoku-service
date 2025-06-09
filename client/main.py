import grpc
import logging

import sys
sys.path.append(r'../generated/auth')
sys.path.append(r'../generated/sudoku')

import auth_pb2
import auth_pb2_grpc
import sudoku_pb2
import sudoku_pb2_grpc

def main():
    # Инициализация соединений с gRPC-сервисами
    try:
        auth_channel = grpc.insecure_channel('localhost:50052')
        auth_client = auth_pb2_grpc.AuthServiceStub(auth_channel)
    except Exception as e:
        logging.fatal(f"Failed to connect to auth service: {e}")
    
    try:
        sudoku_channel = grpc.insecure_channel('localhost:50051')
        sudoku_client = sudoku_pb2_grpc.SudokuServiceStub(sudoku_channel)
    except Exception as e:
        logging.fatal(f"Failed to connect to sudoku service: {e}")

    # Запуск Flask-приложения или другого основного кода
    from handlers import app  # импортируем наш Flask-приложение из handlers.py
    
    print("Server started at :8080")
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()