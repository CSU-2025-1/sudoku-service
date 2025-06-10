from sqlalchemy.orm import Session
from db.models import SudokuModel, SolvedSudokuModel


def create_sudoku(db: Session, sudoku_str: str, difficulty: int) -> SudokuModel:
    sudoku = SudokuModel(sudoku_str=sudoku_str, difficulty=difficulty)
    db.add(sudoku)
    db.commit()
    db.refresh(sudoku)
    return sudoku


def get_sudoku_list(db: Session) -> list[SudokuModel]:
    return db.query(SudokuModel.id, SudokuModel.board_str, SudokuModel.difficulty).all()


def get_sudoku_by_id(db: Session, sudoku_id: int) -> SudokuModel | None:
    return db.query(SudokuModel).filter(SudokuModel.id == sudoku_id).first()


def delete_sudoku(db: Session, sudoku_id: int) -> bool:
    sudoku = db.query(SudokuModel).filter(SudokuModel.id == sudoku_id).first()
    if not sudoku:
        return False
    db.delete(sudoku)
    db.commit()
    return True


def mark_sudoku_solved(db: Session, user_id: int, sudoku_id: int) -> SolvedSudokuModel:
    solved = SolvedSudokuModel(user_id=user_id, sudoku_id=sudoku_id)
    db.add(solved)
    db.commit()
    db.refresh(solved)
    return solved


def get_solved_sudokus(db: Session, user_id: int):
    return db.query(SolvedSudokuModel.sudoku_id).filter(SolvedSudokuModel.user_id == user_id).all()
