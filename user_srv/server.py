import sys
from concurrent import futures
import argparse

import grpc
from loguru import logger
import signal

from common.register import consul
from user_srv.proto import user_pb2_grpc
from user_srv.handler.user import UserServicer
from common.grpc_health.v1 import health_pb2_grpc, health_pb2
from common.grpc_health.v1.health import HealthServicer
from user_srv.settings import settings


def on_exit(signo, frame):
    logger.info("进程中断")
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='192.168.1.103', help='binding ip')
    parser.add_argument('--port', type=int, default=50051, help='listening port')
    args = parser.parse_args()

    logger.add('logs/user_srv_{time}.log')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers =10))

    # 注册用户服务
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    # 注册健康检查
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)

    server.add_insecure_port(f'{args.ip}:{args.port}')

    # 主进程退出信号监听
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    logger.info(f'启动服务 {args.ip}:{args.port}')
    server.start()

    # 注册服务
    register = consul.ConsulRegister(settings.CONSUL_HOST, settings.CONSUL_PORT)
    if not register.register(name=settings.SERVICE_NAME, id=settings.SERVICE_NAME,
                      address=args.ip, port=args.port, tags=settings.SERVICE_TAGS):
        logger.info("服务注册失败")
        sys.exit(0)

    logger.info("服务注册成功")
    server.wait_for_termination()
