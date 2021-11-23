import sys
from concurrent import futures
import argparse
from socket import *
import uuid
from functools import partial

import grpc
from loguru import logger
import signal

sys.path.insert(0, '/home/ws/PycharmProjcets/mxshop_srv')
print(sys.path)

from common.register import consul
from goods_srv.proto import goods_pb2_grpc
from goods_srv.handler.goods import GoodsServicer
from common.grpc_health.v1 import health_pb2_grpc
from common.grpc_health.v1.health import HealthServicer
from goods_srv.settings import settings


register = consul.ConsulRegister(settings.CONSUL_HOST, settings.CONSUL_PORT)


def on_exit(signo, frame, service_id):
    logger.info("进程中断")
    logger.info(f"注销 {service_id} 服务")
    register.deregister(service_id=service_id)
    logger.info("注销成功")
    sys.exit(0)


def get_free_tcp_port():
    tcp = socket()
    tcp.bind(("", 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='192.168.1.103', help='binding ip')
    parser.add_argument('--port', type=int, default=0, help='listening port')
    args = parser.parse_args()

    if args.port == 0:
        args.port = get_free_tcp_port()

    logger.add('logs/goods_srv_{time}.log')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 注册商品服务
    goods_pb2_grpc.add_GoodsServicer_to_server(GoodsServicer(), server)
    # 注册健康检查
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)

    server.add_insecure_port(f'{args.ip}:{args.port}')

    # 主进程退出信号监听
    service_id = str(uuid.uuid1())
    signal.signal(signal.SIGINT, partial(on_exit, service_id=service_id))
    signal.signal(signal.SIGTERM, partial(on_exit, service_id=service_id))

    logger.info(f'启动服务 {args.ip}:{args.port}')
    server.start()

    # 注册服务
    if not register.register(name=settings.SERVICE_NAME, id=service_id,
                      address=args.ip, port=args.port, tags=settings.SERVICE_TAGS):
        logger.info("服务注册失败")
        sys.exit(0)

    logger.info("服务注册成功")
    server.wait_for_termination()

