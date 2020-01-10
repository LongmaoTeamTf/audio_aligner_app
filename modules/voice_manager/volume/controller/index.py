"""
设置音量大小API
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-10-21 11:26:53
@LastEditors: Wang Yao
@LastEditTime: 2019-11-18 16:16:16
"""
import os
import time

from flask import current_app
from flask import Blueprint
from flask import request
from flask import abort
from flask import Response
from flask import session

from library.response.tfexception import TfException
from library.response.tfresponse import TfResponseData
from library.response.tfresponse import TfResponseFile
from library.response.tfresponse import TfResponseString
from library.response.tfwrapper import get_result_wrapper

from ..models.volume import set_audio_volume
from ..models.volume import get_audio_params


GROUP_VOLUME = Blueprint('volume', __name__)



@GROUP_VOLUME.route('/voice/upload', methods=['POST'])
@get_result_wrapper
def upload():
    """
    文件上传
    @param {post} file: 文件
    @return: TfResponseData
    """
    timestamp = str(int(time.time()))
    user_id = timestamp
    audio = request.files.get('file')
    task_id = timestamp
    org_filename = audio.filename
    new_filename = timestamp
    audio_type = org_filename.split(".")[-1]
    org_filepath = os.path.join(current_app.config['APP_UPLOAD_PATH'], new_filename+"."+audio_type)
    http_org_filepath = os.path.join(current_app.config['APP_STATIC_URL_UPLOAD_PATH'], new_filename+"."+audio_type)
    audio.save(org_filepath)

    data = {
        "task_id": task_id, "user_id": user_id,
        "org_filename": org_filename, "new_filename": new_filename,
        "org_filepath": org_filepath, "vol_filepath": "",
        "http_org_filepath": http_org_filepath, 'http_vol_filepath': "",
        "audio_type": audio_type, "volume": "", "create_time": timestamp
    }

    current_app.db.insert_one("voice_manager", "volume", data)
    params = get_audio_params(org_filepath)
    current_app.db.update_one("voice_manager", "volume", {"task_id": task_id}, params)

    return TfResponseData(0, 'success', task_id, user_id)


@GROUP_VOLUME.route('/voice/volume', methods=['POST'])
@get_result_wrapper
def set_volume():
    """
    设置音量
    @param {post} user_id: 用户id, task_id: 任务id, volume: 音量大小
    @return: TfResponseData
    """
    user_id = request.cookies.get('sess')
    task_id = request.params.get('task_id')
    volume = request.params.get('volume')
    cond = {'user_id': user_id, 'task_id': task_id}
    data = current_app.db.find_one('voice_manager', 'volume', cond=cond)
    file_name = data['new_filename']
    audio_type = data['audio_type']
    org_path = data['org_filepath']

    if not volume:
        raise TfException(-1, "volume not set.")

    vol_path = os.path.join(current_app.config['APP_VOLUME_PATH'], file_name+"."+audio_type)
    set_audio_volume(org_path, volume, vol_path)
    http_vol_filepath = os.path.join(current_app.config['APP_STATIC_URL_VOLUME_PATH'], file_name+"."+audio_type)

    cond = {"user_id": user_id, "task_id": task_id}
    values = {"volume": volume, "vol_filepath": vol_path, "http_vol_filepath": http_vol_filepath}
    current_app.db.update_one("voice_manager", "volume", cond, values)

    return TfResponseData(0, 'success', task_id, user_id)


@GROUP_VOLUME.route("/voice/params", methods=['GET', 'POST'])
@get_result_wrapper
def get_params():
    """
    通过task_id, user_id获取音频信息
    @param {post} user_id: 用户id, task_id: 任务id
    @return: TfResponseData
    """
    user_id = request.cookies.get('sess')
    task_id = request.params.get("task_id")

    if not task_id:
        raise TfException(-1, "no task_id")

    cond = {"user_id": user_id, "task_id": task_id}
    data = current_app.db.find_one("voice_manager", "volume", cond=cond)

    return TfResponseData(0, 'success', data, user_id)


@GROUP_VOLUME.route('/voice/download', methods=['GET', 'POST'])
@get_result_wrapper
def download():
    """
    下载文件
    @param {post} user_id: 用户id, task_id: 任务id
    @return: TfResponseFile
    """
    user_id = request.cookies.get('sess')
    task_id = request.params.get("task_id")
    if not task_id:
        raise TfException(-1, "no task_id")

    cond = {"user_id": user_id, "task_id": task_id}
    field = {"vol_filepath": 1}
    data = current_app.db.find_one("voice_manager", "volume", cond=cond, field=field)

    vol_path = data['vol_filepath']
    if not vol_path:
        return abort(Response('no such file.'))

    return TfResponseFile(vol_path)


@GROUP_VOLUME.route('/voice/history', methods=['GET', 'POST'])
@get_result_wrapper
def get_history():
    """
    获取历史列表
    @param {post} user_id: 用户id
    @return: TfResponseData
    """
    user_id = request.cookies.get('sess')
    cond = {"user_id": user_id}
    data = current_app.db.find_all("voice_manager", "volume", cond=cond)

    history_data = []
    for i, item in enumerate(data):
        format_string = "%Y-%m-%d %H:%M:%S"
        time_array = time.localtime(item['create_time'])
        str_date = time.strftime(format_string, time_array)
        tags = ['complete'] if item['volume'] else ['upload']
        data = {
            "key": str(i+1),
            "id": item['task_id'],
            "filename": item['org_filename'],
            "type": item['audio_type'],
            "volume": item['volume'],
            "createtime": str_date,
            "tags": tags
        }
        history_data.append(data)

    return TfResponseData(0, 'success', history_data, user_id)


@GROUP_VOLUME.route('/voice/delete', methods=['DELETE', 'POST'])
@get_result_wrapper
def delete():
    """
    历史列表删除
    @param {delete, post} user_id: 用户id, task_id: 任务id
    @return: TfResponseString
    """
    user_id = request.cookies.get('sess')
    task_id = request.params.get("task_id")
    if not task_id:
        raise TfException(-1, 'no task_id')

    cond = {"user_id": user_id, "task_id": task_id}
    current_app.db.delete_one("voice_manager", "volume", cond)

    return TfResponseString('success')


@GROUP_VOLUME.route('/voice/register', methods=['POST'])
@get_result_wrapper
def register():
    """
    用户注册
    @param {post} email: 邮箱, password: 密码, nickname: 昵称, phone: 电话, prefix: 电话前缀
    @return: TfResponseData
    """
    email = request.params.get("email")
    password = request.params.get("password")
    nickname = request.params.get("nickname")
    phone = request.params.get("phone")
    prefix = request.params.get("prefix")

    data = {
        "id": str(round(time.time())),
        "email": email,
        "password": password,
        "nickname": nickname,
        "phone": phone,
        "prefix": prefix
    }
    current_app.db.insert_one("voice_manager", "user", data)

    user_id = data['id']
    email = data['email']
    token = current_app.tk.get_token(user_id, email)

    return TfResponseData(0, 'success', token, user_id)


@GROUP_VOLUME.route('/voice/login', methods=['POST'])
@get_result_wrapper
def login():
    """
    用户登录
    @param {post} username: 用户名, password: 密码
    @return: TfResponseData
    """
    username = request.params.get("username")
    password = request.params.get("password")

    cond = {"nickname": username}
    field = {"id": 1, "password": 1, "email": 1}
    data = current_app.db.find_one("voice_manager", "user", cond=cond, field=field)

    if not data:
        raise TfException(-1, 'username does not exit.')

    ture_pwd = data['password']
    if password != ture_pwd:
        raise TfException(-1, 'password is wrong.')

    user_id = data['id']
    email = data['email']
    token = current_app.tk.get_token(user_id, email)

    return TfResponseData(0, 'success', token, user_id)
