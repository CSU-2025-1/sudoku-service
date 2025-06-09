import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/sudoku_db")


settings = Settings()