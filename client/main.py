from handlers import app


def main():
    print("Server started at :8080")
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
