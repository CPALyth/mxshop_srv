import sys
from concurrent import futures
import argparse

import grpc
from loguru import logger
import signal

from user_srv.proto import user_pb2_grpc
from user_srv.handler.user import UserServicer


def on_exit(signo, frame):
    logger.info("进程中断")
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='binding ip')
    parser.add_argument('--port', type=int, default=50051, help='listening port')
    args = parser.parse_args()

    logger.add('logs/user_srv_{time}.log')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers =10))
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    server.add_insecure_port(f'{args.ip}:{args.port}')

    # 主进程退出信号监听
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    logger.info(f'启动服务 {args.ip}:{args.port}')
    server.start()
    server.wait_for_termination()
