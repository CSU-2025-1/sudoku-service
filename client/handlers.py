from flask import Flask
from jwt_token.jwt_check import check_token_valid

app = Flask(__name__)


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
