from fastapi import FastAPI, HTTPException, Request, Depends
import grpc.aio as grpc_async
import grpc
from contextlib import asynccontextmanager
import logging

import sys

sys.path.append('../generated/auth')
sys.path.append('../generated/sudoku')

import auth_pb2
import auth_pb2_grpc
import sudoku_pb2
import sudoku_pb2_grpc

from jwt_token.jwt_check import check_token_valid

app = FastAPI()

auth_client = None
sudoku_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global auth_client, sudoku_client

    # Создаем каналы при старте приложения
    auth_channel = grpc_async.insecure_channel('auth:50052')
    auth_client = auth_pb2_grpc.AuthServiceStub(auth_channel)

    sudoku_channel = grpc_async.insecure_channel('solver:50051')
    sudoku_client = sudoku_pb2_grpc.SudokuServiceStub(sudoku_channel)

    yield

    # Можно закрыть каналы по завершении
    await auth_channel.close()
    await sudoku_channel.close()


app = FastAPI(lifespan=lifespan)


async def get_auth_client():
    if auth_client is None:
        raise HTTPException(status_code=503, detail="Auth service not available")
    return auth_client


async def get_sudoku_client():
    if sudoku_client is None:
        raise HTTPException(status_code=503, detail="Sudoku service not available")
    return sudoku_client


async def verify_token(request: Request):
    token = request.headers.get("Authorization")
    is_token_valid = check_token_valid(token)
    if not is_token_valid:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True


################# ROUTES #################


@app.post("/api/register")
async def handle_register(request: Request, client=Depends(get_auth_client)):
    try:
        data = await request.json()
        username = data["username"]
        password = data["password"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request")

    try:
        response = await client.Register(
            auth_pb2.RegisterRequest(username=username, password=password),
            timeout=5
        )
        return {"success": response.success}
    except grpc.RpcError as e:
        logging.fatal(f'Register error: {e}')
        raise HTTPException(status_code=500, detail=f"Register error")


@app.post("/api/login")
async def handle_login(request: Request, client=Depends(get_auth_client)):
    try:
        data = await request.json()
        username = data["username"]
        password = data["password"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request")

    try:
        response = await client.Login(
            auth_pb2.LoginRequest(username=username, password=password),
            timeout=5
        )
        return {
            "success": response.success,
            "token": response.token,
            "message": ""
        }
    except grpc.RpcError as e:
        logging.fatal(f'Login error: {e}')
        raise HTTPException(status_code=500, detail=f"Login failed")


@app.post("/api/solve")
async def handle_solve(request: Request, client=Depends(get_sudoku_client)):
    await verify_token(request)

    try:
        data = await request.json()
        puzzle = data["Puzzle"]
        is_steps = data["IsSteps"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request")

    try:
        response = await client.Solve(
            sudoku_pb2.SudokuRequest(puzzle=puzzle, isSteps=is_steps),
            timeout=5
        )
        return {"solution": response.solution}
    except grpc.RpcError as e:
        logging.fatal(f'Sudoku solve error: {e}')
        raise HTTPException(status_code=500, detail=f"Sudoku solve error")


@app.get("/api/sudoku")
async def get_sudokus(request: Request, client=Depends(get_sudoku_client)):
    token = request.headers.get('Authorization')
    await verify_token(request)

    try:
        response = await client.GetSudokuList(sudoku_pb2.GetSudokuRequest(token=token), timeout=5)

        sudoku_data = {
            'ids': list(response.ids),
            'boards': list(response.boards),
            'difficulties': list(response.difficulties),
            'is_solved': list(response.isSolved)
        }

        return sudoku_data
    except Exception as e:
        logging.fatal(f'Sudoku get error: {e}')
        raise HTTPException(status_code=500, detail=f"Не удалось получить судоку")


@app.post("/api/check_sudoku")
async def check_sudoku(request: Request, client=Depends(get_sudoku_client)):
    token = request.headers.get('Authorization')
    await verify_token(request)

    try:
        data = await request.json()
        solution = data["Solution"]
        sudoku_id = data["SudokuId"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request")

    try:
        response = await client.CheckSudoku(
            sudoku_pb2.CheckSudokuRequest(solution=solution,
                                          token=token,
                                          sudokuId=sudoku_id),
            timeout=5
        )
        return {"isCorrect": response.isCorrect}
    except grpc.RpcError as e:
        logging.fatal(f'Sudoku check error: {e}')
        raise HTTPException(status_code=500, detail=f"Sudoku check error")
