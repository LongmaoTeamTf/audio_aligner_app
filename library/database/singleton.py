"""
单例类
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-10-21 11:26:53
@LastEditors: Wang Yao
@LastEditTime: 2019-11-17 20:20:36
"""


class Singleton(object):
    """
    @description:单例类
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        args = args or None
        kwargs = kwargs or {}
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
