from concurrent import futures
import logging

import grpc

from user_srv.proto import user_pb2_grpc
from user_srv.handler.user import UserServicer

if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    server.add_insecure_port('127.0.0.1:50051')
    server.start()
    print('grpc服务器运行中...')
    server.wait_for_termination()
