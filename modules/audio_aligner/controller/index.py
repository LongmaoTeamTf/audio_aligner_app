#!/usr/bin/env python
"""
中英文对齐函数
# -*- coding: utf-8 -*-
# @Time    : 2019-11-03 16:35
# @Author  : Longmao
# @Site    :
# @File    : index.py.py
# @Software: PyCharm
"""

import os
import time
from flask import Blueprint, current_app
from flask import request

from library.response import tfexception
from library.response.tfresponse import TfResponseFile, TfResponseData
from library.response.tfwrapper import get_result_wrapper
from modules.audio_aligner.models.english_script import unzip_file
from modules.audio_aligner.models.chinese_script import chinese_aligner
from modules.audio_aligner.models.english_script import english_aligner
GROUP_ALIGNER = Blueprint('aligner', __name__)


@GROUP_ALIGNER.route('/aligner/upload', methods=['POST'])
@get_result_wrapper
def upload():
    """
    @description:文件上传
    @:param {post}
    :return:
    """
    user_id = request.cookies.get('sess')

    now = time.time()
    timel = time.localtime(now)
    format_time = time.strftime("%Y-%m-%d %H:%M:%S", timel)
    file = request.files['file']
    if not user_id:
        user_id = str(int(now))

    try:
        date = format_time
        ori_filename = file.filename
        new_filename = str(now)
        task_id = str(now)
        file_type = os.path.splitext(ori_filename)[-1]
        ori_filepath = os.path.join(current_app.config['APP_UPLOAD_PATH'], new_filename + file_type)
        print(ori_filepath)
        ali_filepath = os.path.join(current_app.config['APP_UPLOAD_PATH'], new_filename + '.txt')
        http_org_filepath = os.path.join(current_app.config['APP_STATIC_URL_UPLOAD_PATH'], new_filename, ".",
                                         file_type)
        file.save(ori_filepath)
        current_app.logger.info('upload success')

        data = {
            "task_id": task_id, "user_id": user_id,
            "org_filename": ori_filename, "new_filename": new_filename,
            "org_filepath": ori_filepath, "ali_filepath": ali_filepath,
            "http_org_file_filepath": http_org_filepath, "http_ali_filepath": '',
            'upload_time': date, 'tags': 'unfinished', 'process': 0, 'language': '',
            'start': 0, 'success_': 0, 'failed': 0, 'result': ''
        }
        current_app.db.insert_one('Aligner', 'ChineseAli', data)
        return TfResponseData(0, 'success', task_id, user_id)
    except Exception as exp:
        current_app.logger.error('uplaod failed ! . please try again...')
        current_app.logger.error(exp)
        return TfResponseData('failed', 0, code=tfexception.TASK_CREATE_FAILED)


@GROUP_ALIGNER.route('/aligner/display', methods=['POST', 'GET'])
@get_result_wrapper
def display():
    """
    展示函数
    """
    user_id = request.cookies.get('sess')
    print(user_id)
    page_no = request.params.get("page")
    field = {'_id': 0, 'org_filename': 1, 'upload_time': 1, 'tags': 1, 'task_id': 1, 'start': 1, 'success_': 1,
             'failed': 1, 'language': 1, 'result': 1}
    ret = current_app.db.find_all(name='Aligner', collection='ChineseAli', cond={'user_id': user_id}, field=field,
                                  page_no=page_no)
    ret = list(ret)

    return TfResponseData(0, 'success', ret, 0)


@GROUP_ALIGNER.route('/aligner/chinese', methods=['POST', 'GET'])
@get_result_wrapper
def chinese():
    # print('进入中文对齐。。。')
    """
    中文对齐函数
    """
    task_id = request.params.get('id')
    print(task_id)
    ali_path = current_app.db.find_all('Aligner', 'ChineseAli', {'task_id': task_id}, {'ali_filepath': 1})
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'start': 1, 'language': 'chinese'})
    ali_path = list(ali_path)[0]['ali_filepath']
    audio_path, text_path = unzip_file(task_id)
    print(audio_path, text_path)
    try:
        res = chinese_aligner(task_id, ali_path, text_path, audio_path)
    # current_app.db.update_one('Aligner','ChineseAli',{'task_id':id},{'result':res})
        current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'success_': 1})
    except Exception as error:
        current_app.db.update_one('Aligner','ChineseAli', {'task_id':task_id}, {'failed':1})
    return TfResponseData(0, 'success', res, 0)


@GROUP_ALIGNER.route('/aligner/english', methods=['POST', 'GET'])
@get_result_wrapper
def english():
    """
    英文对齐函数接口
    :return:
    """
    task_id = request.params.get('id')
    print(task_id)
    ali_path = current_app.db.find_all('Aligner', 'ChineseAli', {'task_id': task_id}, {'ali_filepath': 1})
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'start': 1, 'language': 'english'})
    ali_path = list(ali_path)[0]['ali_filepath']
    audio_path, text_path = unzip_file(task_id)
    print(audio_path,text_path)
    try:
        res = english_aligner(task_id, ali_path, text_path, audio_path)
        current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'success_': 1})
    except Exception as error:
        current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'failed': 1})
    return TfResponseData(0, 'success', res, 0)


@GROUP_ALIGNER.route('/aligner/percent', methods=['POST', 'GET'])
@get_result_wrapper
def process():
    """
    展示进程函数
    :return:
    """
    task_id = request.json.get('id')
    process_info = current_app.db.find_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 1})
    process_status = process_info['process']
    return TfResponseData(0, 'success', process_status, 0)


@GROUP_ALIGNER.route('/aligner/download', methods=['POST', 'GET'])
@get_result_wrapper
def download():
    """
    下载函数
    :return:
    """
    task_id = request.params.get('id')
    print(task_id)
    data = current_app.db.find_one("Aligner", 'ChineseAli', {'task_id': task_id}, {'ali_filepath': 1})
    ali_path = data['ali_filepath']
    print(ali_path)
    if not ali_path:
        return 'no such file'
    return TfResponseFile(ali_path)


@GROUP_ALIGNER.route('/aligner/check', methods=['POST', 'GET'])
@get_result_wrapper
def check():
    """
    查看任务状态
    :return:
    """
    task_id = request.params.get('id')
    data = current_app.db.find_one('Aligner', 'ChineseAli', {'task_id': str(task_id)}, {'_id': 0, 'start': 1, 'success_': 1, 'failed': 1})
    return TfResponseData(0, 'success', data, 0)
