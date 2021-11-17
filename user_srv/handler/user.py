import time
from datetime import date

import grpc
from loguru import logger
from passlib.hash import pbkdf2_sha256
from google.protobuf import empty_pb2

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
        logger.info("GetUserList")
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
        logger.info("GetUserById")
        user = User.get_or_none(User.id == request.id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('用户不存在')
            return user_pb2.UserInfoResponse()
        return self.convert_user_to_rsp(user)

    @logger.catch
    def GetUserByMobile(self, request: user_pb2.MobileRequest, context):
        """通过手机号查询用户"""
        logger.info("GetUserByMobile")
        user = User.get_or_none(User.mobile == request.mobile)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('用户不存在')
        return self.convert_user_to_rsp(user)

    @logger.catch
    def CreateUser(self, request: user_pb2.CreateUserInfo, context):
        """新建用户"""
        logger.info("CreateUser")
        user = User.get_or_none(User.mobile == request.mobile)
        if user:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('用户已存在')
            return user_pb2.UserInfoResponse()
        user = User(
            nick_name=request.nickName,
            mobile=request.mobile,
            password=pbkdf2_sha256.hash(request.password),
        )
        user.save()
        return self.convert_user_to_rsp(user)

    @logger.catch
    def UpdateUser(self, request: user_pb2.UpdateUserInfo, context):
        """更新用户"""
        logger.info("UpdateUser")
        user = User.get(User.id == request.id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('用户不存在')
            return user_pb2.UserInfoResponse()
        user.nick_name = request.nickName
        user.gender = request.gender
        user.birthday = date.fromtimestamp(request.birthDay)
        user.save()
        return empty_pb2.Empty()

    @logger.catch
    def CheckPassword(self, request: user_pb2.UpdateUserInfo, context):
        """检查密码"""
        logger.info("CheckPassword")
        return user_pb2.CheckResponse(success=pbkdf2_sha256.verify(request.password, request.encryptedPassword))