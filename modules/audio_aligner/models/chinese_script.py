"""
中文对齐脚本
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-11-01 11:11
# @Author  : LongMao
# @Site    :
# @File    : ChineseAligner.py
# @Software: PyCharm

import os
import re
import json
import subprocess
from functools import reduce
from librosa import sequence
from flask import current_app


# @get_result_wrapper
def dictionary_build(text_path):
    """
    建立字典
    :param text_path:
    :return:
    """
    current_app.logger.info('dictionary building...')
    print(text_path)
    with open(text_path, 'r', encoding='utf-8') as file:
        print('rrrrrr')
        data = file.read()
        print('1111')
        pattern = re.compile(u"[\u4e00-\u9fa5]")
        print('222')
        temp_dic = re.findall(pattern, data)
        print('333')
        ret = []
        for item in temp_dic:
            ret.extend(item)
        word_list = [i for i in ret]
        unrepeated_word_list = list(set(word_list))
        word_diction = {}
        for i, word in enumerate(unrepeated_word_list):
            word_diction[word] = i
        res = {'dict': word_diction, 'txt': word_list}
        # res = word_diction
    return res


def kaldi_ali(task_id, audio_path):
    """
    使用kaldi完成单词级别打点
    :param task_id:
    :param audio_path:
    :return:
    """
    print(task_id)
    os.chdir('/root/tools/kaldi/egs/aidatatang_200zh/s5')
    cmd = "python align/run.py chinese {} ".format(audio_path)
    status, ret = subprocess.getstatusoutput(cmd)
    print(status)
    ret = ret.split('\n')[-1]
    ret = json.loads(ret)
    word_ali = ret['ctm']

    return word_ali


# @get_result_wrapper
def text_process(task_id, text_path, audio_path):
    """
    文本处理函数
    :param task_id:
    :param text_path:
    :param audio_path:
    :return:
    """
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 25})

    res = dictionary_build(text_path)
    print('tttt')
    dictionary = res['dict']
    src_text_list = res['txt']
    word_ali = kaldi_ali(task_id, audio_path)
    asr_text_list = []
    asr_code_list = []
    src_code_list = []
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 50})
    relationship = {}
    start = 0
    for number, i in enumerate(word_ali):
        asr_text_list += [x for x in i['word']]
        for k in range(len(i['word'])):
            relationship[start + k] = number
        start += len(i['word'])
    for i in src_text_list:
        src_code_list.append(dictionary[i])
    for i in asr_text_list:
        if i not in dictionary.keys():
            asr_code_list.append(-1)
        else:
            asr_code_list.append(dictionary[i])
    _, wrap = sequence.dtw(src_code_list, asr_code_list)
    res = {'wrap': wrap, 'relationship': relationship}

    return res


def find_start_location(task_id, text_path):
    """
    找到每段的起始位置
    :param task_id:
    :param text_path:
    :return:
    """
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 75})
    start_location = [0]
    with open(text_path, 'r',encoding='utf-8') as file:
        data = file.read()
        split_text = data.split('#')
        for item in split_text:
            if item != '':
                pattern = re.compile(u"[\u4e00-\u9fa5]")
                temp = re.findall(pattern, item)
                item = reduce(lambda x, y: x + y, temp)
                start_location.append(start_location[-1] + len(item) - 1)

    return start_location


def chinese_aligner(task_id, ali_path, text_path, audio_path):
    """
    中文对齐的核心脚本
    :param id:
    :param ali_path:
    :param text_path:
    :param audio_path:
    :return:
    """
    print('11')
    word_ali = kaldi_ali(task_id, audio_path)
    print('22')
    res = text_process(task_id, text_path, audio_path)
    print('333')
    wrap = res['wrap']
    relationship = res['relationship']
    start_location = find_start_location(task_id, text_path)
    print('444')
    asr_location = []
    for num in start_location:
        temp = [tmp[1] for tmp in wrap if tmp[0] == num][0]
        asr_location.append(temp)
    time = []
    print('555')
    for num in asr_location:
        time.append(relationship[num])
    start_time = []
    for num in time:
        start_time.append(word_ali[num]['start'])
    print('666')
    with open(text_path, 'r',encoding='utf-8') as file:
        data = file.read()
        split_text = data.split('#')
    res = {}
    print('777')
    for num,_ in enumerate(split_text):
        temp = '[' + str(start_time[num]) + ']' + str(split_text[num])
        res[num] = temp
    print('888')
    with open(ali_path, 'w',encoding='utf-8') as file:
        for num in res:
            file.write(res[num])
            file.write('\n')
    print('999')
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 100})
    return res
