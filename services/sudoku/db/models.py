from db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class SudokuModel(Base):
    __tablename__ = "sudokus"
    id = Column(Integer, primary_key=True, index=True)
    board_str = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)

    solved_by = relationship("SolvedSudokuModel", back_populates="sudoku")


class SolvedSudokuModel(Base):
    __tablename__ = "solved_sudokus"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    sudoku_id = Column(Integer, ForeignKey("sudokus.id"), index=True, nullable=False)

    sudoku = relationship("SudokuModel", back_populates="solved_by")