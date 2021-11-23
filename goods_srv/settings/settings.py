from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin

from loguru import logger

import nacos


class ReconnectMysqlDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


NACOS = {
    "Host": "192.168.1.103",
    "Port": 8848,
    "NameSpace": "db58866d-b526-4cf1-911d-a7aa072b413f",
    "User": "nacos",
    "Password": "nacos",
    "DataId": "goods_srv.json",
    "Group": "dev",
}

client = nacos.NacosClient("{}:{}".format(NACOS["Host"], NACOS["Port"]), namespace=NACOS["NameSpace"],
                           username=NACOS["User"], password=NACOS["Password"])

import json

json_data = json.loads(client.get_config(NACOS["DataId"], NACOS["Group"]))
logger.info(json_data)


# 监控配置文件的变化
def test_cb(args):
    logger.info("配置文件产生变化")
    json_data = json.loads(args.get('raw_content'))
    logger.info(json_data)
    # 重新赋值全局变量
    global CONSUL_HOST, CONSUL_PORT, SERVICE_NAME, SERVICE_TAGS, DB
    CONSUL_HOST = json_data["consul"]["host"]
    CONSUL_PORT = json_data["consul"]["port"]
    SERVICE_NAME = json_data["name"]
    SERVICE_TAGS = json_data["tags"]
    DB = ReconnectMysqlDatabase(json_data["mysql"]["db"], host=json_data["mysql"]["host"],
                                port=json_data["mysql"]["port"],
                                user=json_data["mysql"]["user"], password=json_data["mysql"]["password"])


client.add_config_watcher(NACOS["DataId"], NACOS["Group"], test_cb)

CONSUL_HOST = json_data["consul"]["host"]
CONSUL_PORT = json_data["consul"]["port"]

SERVICE_NAME = json_data["name"]
SERVICE_TAGS = json_data["tags"]

DB = ReconnectMysqlDatabase(json_data["mysql"]["db"], host=json_data["mysql"]["host"], port=json_data["mysql"]["port"],
                            user=json_data["mysql"]["user"], password=json_data["mysql"]["password"])

