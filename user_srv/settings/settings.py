from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectMysqlDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


MYSQL_DB = "mxshop_user_srv"
MYSQL_HOST = "192.168.1.103"
MYSQL_PORT = 3306
MYSQL_USER = "ws"
MYSQL_PASSWORD = "123456"


DB = ReconnectMysqlDatabase(MYSQL_DB, host=MYSQL_HOST, port=MYSQL_PORT,
                            user=MYSQL_USER, password=MYSQL_PASSWORD)