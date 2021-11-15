from peewee import *
from user_srv.settings import settings

db = settings.DB

class BaseModel(Model):
    class Meta:
        database = settings.DB


class User(BaseModel):
    # db值, py值
    GENDER_CHOICES = (

        ("female", "女"),
        ("male", "男")
    )
    ROLE_CHOICES = (
        (1, "普通用户"),
        (2, "管理员")
    )
    mobile = CharField(verbose_name='手机号', unique=True)
    password = CharField(verbose_name='密码')
    nick_name = CharField(verbose_name='昵称', null=True)
    head_url = CharField(verbose_name='头像', null=True)
    birthday = DateField(verbose_name='生日', null=True)
    address = CharField(verbose_name='地址', null=True)
    desc = TextField(verbose_name='个人简介', null=True)
    gender = CharField(verbose_name='性别', choices=GENDER_CHOICES, null=True)
    role = IntegerField(verbose_name='用户角色', choices=ROLE_CHOICES, default=1)


if __name__ == '__main__':
        db.create_tables([User])