"""
mongo数据库
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-10-21 11:26:53
@LastEditors: Wang Yao
@LastEditTime: 2019-11-17 16:20:36
"""

import pymongo

from .singleton import Singleton


class TfMongo(Singleton):
    """
    mongo数据库操作类
    """

    def __init__(self, host: str, port: int):
        """
        :param host:数据库ip
        :param port:数据库端口
        """
        self._host = host
        self._port = port
        self.client = pymongo.MongoClient(host=self._host, port=self._port)

    def find_all(self, name: str, collection: str, cond=None, field=None, page_no=0, page_size=20) -> object:
        """
        获取所有数据
        :param page_size: 每页文档数
        :param page_no: 页码
        :param name:数据库名称
        :param collection: 数据库集合名称
        :param cond:查询条件
        :param field:查询字段
        :return: dict
        """
        if cond is None:
            cond = {}
        if field is None:
            field = {'_id': 0}
        _collection = self.client[name][collection]
        if field:
            if page_no:
                data = _collection.find(cond, field).limit(page_size).skip(page_size*(page_no-1))
            else:
                data = _collection.find(cond, field)
        else:
            if page_no:
                data = _collection.find(cond).limit(page_size).skip(page_size*(page_no-1))
            else:
                data = _collection.find(cond)
        return data

    def find_one(self, name: str, collection: str, cond=None, field=None) -> object:
        """
        获取一条数据
        :param name:数据库名称
        :param collection: 数据库集合名称
        :param cond:查询条件
        :param field:查询字段
        :return: dict
        """
        if cond is None:
            cond = {}
        if field is None:
            field = {'_id': 0}
        _collection = self.client[name][collection]
        if field:
            data = _collection.find_one(cond, field)
        else:
            data = _collection.find_one(cond)
        return data

    def insert_one(self, name: str, collection: str, data: dict):
        """
        插入一条数据
        :param name:数据库名称
        :param collection:集合名称
        :param data:返回数据
        """
        _collection = self.client[name][collection]
        _collection.insert_one(data)

    def delete_one(self, name: str, collection: str, cond: dict):
        """
        删除一条数据
        :param name:数据库名称
        :param collection:集合名称
        :param cond:查询条件
        """
        _collection = self.client[name][collection]
        _collection.delete_one(cond)

    def update_one(self, name: str, collection: str, cond: dict, data: dict):
        """
        更新一条数据
        :param name:数据库名称
        :param collection:集合名称
        :param cond:查询条件
        :param data:
        """
        _collection = self.client[name][collection]
        _collection.update_one(cond, {"$set": data})

    def __del__(self):
        """
        :Description: 关闭数据库
        """
        self.client.close()
