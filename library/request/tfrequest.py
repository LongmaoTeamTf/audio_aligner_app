"""
请求封装
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 20:36:16
@LastEditors: Wang Yao
@LastEditTime: 2019-11-17 21:24:58
"""
from flask import request


class TfRequest(object):
    """
    请求处理
    """
    def __init__(self):
        pass

    @staticmethod
    def get_params():
        """
        请求的参数融合
        """
        if request.json:
            request.params = request.json
        if request.form:
            request.params = request.form
        if request.args:
            request.params = request.args
