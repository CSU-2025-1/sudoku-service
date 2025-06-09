import grpc
from concurrent import futures

import sys
sys.path.append(r'../../generated/auth')

import auth_pb2, auth_pb2_grpc

# Временное хранилище пользователей (в реальности — база данных)
users = {}  # username -> password

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def Register(self, request, context):
        if request.username in users:
            return auth_pb2.RegisterResponse(
                success=False,
                message="User already exists"
            )
        users[request.username] = request.password
        return auth_pb2.RegisterResponse(
            success=True,
            message="Registration successful"
        )

    def Login(self, request, context):
        password = users.get(request.username)
        if password is None or password != request.password:
            return auth_pb2.LoginResponse(
                success=False,
                token=""
            )
        token = "dummy-token-for-" + request.username  # В реальности — JWT или другой токен.
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