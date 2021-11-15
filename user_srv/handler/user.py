import time

import grpc
from loguru import logger

from ..model.models import User
from ..proto import user_pb2, user_pb2_grpc


class UserServicer(user_pb2_grpc.UserServicer):

    def convert_user_to_rsp(self, user):
        # 将user的model对象 转换成 message对象
        user_info_rsp = user_pb2.UserInfoResponse()

        user_info_rsp.id = user.id
        user_info_rsp.passWord = user.password
        user_info_rsp.mobile = user.mobile
        user_info_rsp.role = user.role

        if user.nick_name:
            user_info_rsp.nickName = user.nick_name

        if user.gender:
            user_info_rsp.gender = user.gender

        if user.birthday:
            user_info_rsp.birthDay = int(time.mktime(user.birthday.timetuple()))
        return user_info_rsp


    @logger.catch
    def GetUserList(self, request: user_pb2.PageInfo, context):
        # 获取用户的列表
        rsp = user_pb2.UserListResponse()

        users = User.select()
        rsp.total = users.count()

        start = 0
        per_page_nums = 10
        if request.pSize:
            per_page_nums = request.pSize
        if request.pn:
            start = per_page_nums * (request.pn - 1)

        users = users.limit(per_page_nums).offset(start)

        for user in users:
            user_info_rsp = self.convert_user_to_rsp(user)
            rsp.data.append(user_info_rsp)
        return rsp


    @logger.catch
    def GetUserById(self, request: user_pb2.IdRequest, context):
        """通过ID查询用户"""
        user = User.get_or_none(User.id == request.id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('用户不存在')
            return user_pb2
        return self.convert_user_to_rsp(user)