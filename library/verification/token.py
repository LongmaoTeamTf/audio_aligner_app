"""
user token
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 15:21:11
@LastEditors: Wang Yao
@LastEditTime: 2019-11-17 21:17:19
"""
from functools import wraps
from flask import request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from library.response.tfexception import TfException
from library.request.tfrequest import TfRequest


class TfToken(object):
    """
    Token类
    """

    def __init__(self, secret_key: str, expires_in: int):
        self._secret_key = secret_key
        self._expires_in = expires_in
        self.serializer = Serializer(secret_key, expires_in=expires_in)

    def get_token(self, user_id: str, email: str) -> str:
        """
        生成token
        @param user_id: 用户id, email: 邮箱
        @return: token
        :param email: 邮箱
        """
        data = {'user_id': user_id, 'email': email}
        token = self.serializer.dumps(data).decode()
        return token

    def decode_token(self, token: str) -> dict:
        """
        token解码
        @param token
        @return: data
        """
        try:
            data = self.serializer.loads(token)
        except BadData:
            code, msg = -3, "token decoded error."
            raise TfException(code, msg)
        return data

    def check_token(self, token):
        """
        校验token
        @param token
        @return: token_data
        """
        if token == 'null':
            code, msg = -3, "please login first."
            raise TfException(code, msg)
        token_data = self.decode_token(token)
        return token_data


def login_check(func):
    """
    登录校验修饰器
    @param func: API函数
    @return: func
    """

    @wraps(func)
    def wrapper(*args, **kw):
        TfRequest().get_params()
        if not request.params.get('token'):
            raise TfException(-3, "please login first.")
        return func(*args, **kw)

    return wrapper
