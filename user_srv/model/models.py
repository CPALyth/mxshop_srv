from peewee import *
from user_srv.settings import settings


class BaseModel(Model):
    class Meta:
        database = settings.DB


class User(BaseModel):
    mobile = CharField(verbose_name='手机号', unique=True)
    password =