from datetime import datetime

from peewee import *
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin
from playhouse.mysql_ext import JSONField


class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


db = ReconnectMySQLDatabase("mxshop_goods_srv", host="192.168.1.103",
                            port=3306, user="ws", password="123456")

class BaseModel(Model):
    add_time = DateTimeField(verbose_name="添加时间", default=datetime.now)
    is_deleted = BooleanField(verbose_name="是否删除", default=False)
    update_time = DateTimeField(verbose_name="更新时间", default=datetime.now)

    def save(self, *args, **kwargs):
        #判断这是一个新添加的数据还是更新的数据
        if self._pk is not None:
            #这是一个新数据
            self.update_time = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def delete(cls, permanently=False): #permanently表示是否永久删除
        if permanently:
            return super().delete()
        else:
            return super().update(is_deleted=True)

    def delete_instance(self, permanently=False, recursive=False, delete_nullable=False):
        if permanently:
            return self.delete(permanently).where(self._pk_expr()).execute()
        else:
            self.is_deleted = True
            self.save()

    @classmethod
    def select(cls, *fields):
        return super().select(*fields).where(cls.is_deleted==False)

    class Meta:
        database = db


class Category(BaseModel):
    # 目录
    parent = ForeignKeyField('self', null=True)
    name = CharField(verbose_name='名称')
    level = IntegerField(verbose_name='级别')
    is_tab = BooleanField(verbose_name='是否显示在首页TAB', default=False)


class Brand(BaseModel):
    # 品牌
    name = CharField(verbose_name='名称', unique=True)
    logo = CharField(verbose_name='图标', null=True, default='')


class Goods(BaseModel):
    # 商品
    category = ForeignKeyField(Category, on_delete='CASCADE')
    brand = ForeignKeyField(Brand, on_delete='CASCADE')
    on_sale = BooleanField(verbose_name='是否上架')
    goods_sn = CharField(verbose_name='商品唯一货号')
    name = CharField(verbose_name='商品名')
    click_num = IntegerField(verbose_name='点击数', default=0)
    sold_num = IntegerField(verbose_name='商品销售量', default=0)
    fav_num = IntegerField(verbose_name='收藏数', default=0)
    market_price = FloatField(verbose_name='市场价格', default=0)
    shop_price = FloatField(verbose_name='本店价格', default=0)
    goods_brief = CharField(verbose_name='商品简短描述')
    ship_free = BooleanField(verbose_name='是否包邮', default=True)
    images = JSONField(verbose_name='商品轮播图')
    desc_images = JSONField(verbose_name='详情页图片')
    goods_front_image = CharField(verbose_name='封面图')
    is_new = BooleanField(verbose_name='是否新品', default=False)
    is_hot = BooleanField(verbose_name='是否热销', default=False)


class GoodsCategoryBrand(BaseModel):
    # 品牌分类
    category = ForeignKeyField(Category)
    brand = ForeignKeyField(Brand)

    class Meta:
        indexs = (
            (("category", "brand"), True),  # 联合索引, 第二个参数为True代表唯一
        )


class Banner(BaseModel):
    # 轮播的商品
    image = CharField(verbose_name='图片url', default='')
    url = CharField(verbose_name='访问url', default='')
    index = IntegerField(verbose_name='轮播顺序', default=0)


if __name__ == '__main__':
    db.create_tables([Category, Goods, Brand, GoodsCategoryBrand, Banner])