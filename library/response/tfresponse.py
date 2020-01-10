"""
TfResponse封装
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 15:21:11
@LastEditors: Wang Yao
@LastEditTime: 2019-11-17 20:47:28
"""
import os
from flask import send_file
from flask import make_response
from flask import jsonify


class TfResponse(object):
    """
    Response基类
    """

    def __init__(self):
        pass

    def processer(self):
        """
        响应处理
        """
        pass


class TfResponseData(TfResponse):
    """
    携带数据的Response
    """

    def __init__(self, code, msg, data, sess):
        super().__init__()
        self._code = code
        self._msg = msg
        self._data = data
        self._sess = sess

    def processer(self):
        resp_data = {'code': self._code, 'msg': self._msg, 'data': self._data}
        resp = make_response(jsonify(resp_data))
        resp.set_cookie("sess", str(self._sess))
        return resp


class TfResponseFile(TfResponse):
    """
    文件下载的Response
    """

    def __init__(self, filepath):
        super().__init__()
        self._filepath = filepath

    def processer(self):
        response = make_response(send_file(self._filepath, as_attachment=True))
        basename = os.path.basename(self._filepath)
        response.headers["Content-Disposition"] = "attachment; filename={}".format(basename.encode().decode('latin-1'))
        return response


class TfResponseString(TfResponse):
    """
    字串的Response
    """

    def __init__(self, string):
        super().__init__()
        self._string = string

    def processer(self):
        return self._string
