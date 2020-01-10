"""
修饰器
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 15:21:11
@LastEditors: Wang Yao
@LastEditTime: 2019-11-18 17:00:07
"""
import time
import traceback
from functools import wraps
from flask import current_app
from werkzeug.exceptions import HTTPException
from ..request.tfrequest import TfRequest
from .tfexception import TfException


def get_result_wrapper(func):
    """
    异常获取
    @param func: API函数
    @return: func
    """
    @wraps(func)
    @logger_wrapper(func.__name__)
    def wrapper(*args, **kw):
        try:
            resp_obj = func(*args, **kw)
            return resp_obj
        except HTTPException as exc:
            raise exc
        except TfException as exc:
            return TfException(exc.get_code(), traceback.format_exc())
        except Exception:
            return TfException(-1, traceback.format_exc())
    return wrapper


def logger_wrapper(name):
    """
    日志修饰器
    @param name: API函数
    @return: func
    """
    def logger(func):
        @wraps(func)
        def wrapper(*args, **kw):
            start = time.time()
            current_app.logger.info("{} Start.".format(name))
            TfRequest.get_params()
            resp = func(*args, **kw)
            end = time.time()
            if isinstance(resp, TfException):
                current_app.logger.error(
                    "{} Error. Code: {}. Msg: {}.".format(name, resp.get_code(), resp.get_msg()))
            else:
                current_app.logger.info("{} Success.".format(name))
            current_app.logger.info("{} Stop. Cost Time: {}".format(name, round(end-start, 2)))
            return resp.processer()
        return wrapper
    return logger
