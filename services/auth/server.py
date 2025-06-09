import grpc
from concurrent import futures
from db.database import get_db
from crud import users as crud_users
from jwt import jwt_gen

import sys
sys.path.append(r'../../generated/auth')

import auth_pb2, auth_pb2_grpc

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def Register(self, request, context):
        db = next(get_db())
        user = crud_users.get_user_by_name(db, request.username)
        if user is not None:
            return auth_pb2.RegisterResponse(
                success=False,
                message="User already exists"
            )
        created_user = crud_users.create_user(db, request.username, request.password)
        return auth_pb2.RegisterResponse(
            success=True,
            message="Registration successful"
        )

    def Login(self, request, context):
        username = request.username
        db = next(get_db())
        user = crud_users.get_user_by_name(db, username)
        password = user.password
        if password is None or password != request.password:
            return auth_pb2.LoginResponse(
                success=False,
                token=""
            )
        token = jwt_gen.generate_jwt(username)
        return auth_pb2.LoginResponse(
            success=True,
            token=token
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50052')
    print("Auth service listening on :50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()