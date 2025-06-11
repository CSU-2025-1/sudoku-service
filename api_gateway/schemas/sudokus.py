from pydantic import BaseModel


class SolveSudokuRequest(BaseModel):
    Puzzle: str
    IsSteps: bool


class CheckSudokuRequest(BaseModel):
    Solution: str
    SudokuId: int