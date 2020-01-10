"""
异常处理
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 19:08:16
@LastEditors: Wang Yao
@LastEditTime: 2019-11-18 16:07:07
"""

from flask import jsonify

TASK_CREATE_FAILED = 1001


class TfException(Exception):
    """
    异常处理类
    """
    def __init__(self, code: int, msg: str):
        super().__init__()
        self._code = code
        self._msg = msg

    def get_code(self):
        """
        获取code
        @return: _code
        """
        return self._code

    def get_msg(self):
        """
        获取msg
        @return: _msg
        """
        return self._msg

    def processer(self):
        """
        处理
        @return: str
        """
        if self._code == -1:
            exp = {"code": self._code, "msg": self._msg}
        elif self._code == -2:
            exp = {"code": self._code, "msg": self._msg}
        else:
            exp = {"code": self._code, "msg": self._msg}
        return jsonify(exp)
