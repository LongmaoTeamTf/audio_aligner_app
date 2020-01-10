"""
英文对齐脚本
"""
import os
import re
import json
import zipfile

import subprocess
from librosa import sequence
from flask import current_app


def dictionary_build(text_path):
    """
    :param text_path:
    :return:
    """
    current_app.logger.info('dictionary building...')
    with open(text_path,'r',encoding='utf-8') as file:
        data = file.read()
        data = english_filter(data)  # str 将文章中所有的英文单词过滤出来
        word_list = list(set(data))
    word_diction = {}
    for num, word in enumerate(word_list):
        word_diction[word] = num
    res = {'dict': word_diction, 'text': data}
    return res  # 返回值是字典。每个英文单词对应的重新编码 以及过滤之后的英文


def english_filter(string):
    """
    英文分词
    :param string:
    :return:
    """
    filtrate = re.compile('[a-zA-Z]+')
    filtrate_str = filtrate.findall(string)
    return filtrate_str


def kaldi_ali(audio_path):
    """
    kaldi单词级别对齐
    :param audio_path:
    :return:
    """
    os.chdir('/root/tools/kaldi/egs/aidatatang_200zh/s5')
    cmd = "python align/run.py english {}".format(audio_path)
    _, ret = subprocess.getstatusoutput(cmd)
    ret = ret.split('\n')[-1]
    ret = json.loads(ret)
    word_ali = ret['ctm']
    return word_ali


def text_process(task_id, text_path,word_ali):
    """
    文本处理函数
    :param task_id:
    :param text_path:
    :param audio_path:
    :return:
    """
    res = dictionary_build(text_path)
    dictionary = res['dict']  #
    src_text_list = res['text']  #
    # word_ali = kaldi_ali(audio_path)
    word_ali = word_ali
    asr_text_list = []
    asr_code_list = []
    src_code_list = []

    for _, val in enumerate(word_ali):
        asr_text_list.append(val['word'].lower())

    for num in src_text_list:
        src_code_list.append(dictionary[num])

    for num in asr_text_list:
        if num not in dictionary.keys():
            asr_code_list.append(-1)
        else:
            asr_code_list.append(dictionary[num])
    _, wrap = sequence.dtw(src_code_list, asr_code_list)
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 50})
    return wrap


def find_start_location(task_id,text_path):
    """
    找到文件的起始位置
    :param text_path:
    :return:
    """
    start_location = [0]
    pattern = re.compile('[a-zA-Z]+')
    with open(text_path, 'r', encoding='utf-8') as file:
        data = file.read()
        split_text = data.split('#')
        len_ = 0
        for item in split_text:
            if item != '':
                res = pattern.findall(item)
                len_ += len(res)
                start_location.append(start_location[-1] + len(res))
    start_location[-1] = len_ - 1
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 75})
    return start_location  #


def english_aligner(task_id, ali_path, text_path, audio_path):
    """
    英文对齐函数
    :param id:
    :param ali_path:
    :param text_path:
    :param audio_path:
    :return:
    """
    print('111')
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 25})
    print('222')
    word_ali = kaldi_ali(audio_path)
    print('333')
    wrap = text_process(task_id, text_path, word_ali)
    print('444')
    start_location = find_start_location(task_id, text_path)
    print('555')
    asr_location = []
    for num in start_location:
        temp = [tem[1] for tem in wrap if tem[0] == num][0]
        asr_location.append(temp)
    start_time = []
    print('666')
    for num in asr_location:
        start_time.append(word_ali[num]['start'])
    print('777')
    with open(text_path, 'r', encoding='utf-8') as file:
        data = file.read()
        split_text = data.split('#')
    res = {}
    print('888')
    for num, _ in enumerate(split_text):
        temp = '[' + str(start_time[num]) + ']' + str(split_text[num])
        res[num] = temp
    with open(ali_path, 'w', encoding='utf-8') as file:
        for i in res:
            file.write(res[i])
            file.write('\n')
    print('999')
    current_app.db.update_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'process': 100})
    return res


def unzip_file(task_id):
    """
    解压文件函数
    :param task_id:
    :return:
    """
    ori_filepath = current_app.db.find_one('Aligner', 'ChineseAli', {'task_id': task_id}, {'org_filepath': 1})
    org_filepath = ori_filepath['org_filepath']
    dirname = os.path.join(os.path.dirname(org_filepath), os.path.splitext(os.path.basename(org_filepath))[0])
    os.makedirs(dirname)
    zip_file = zipfile.ZipFile(org_filepath)
    # 将文件解压到上传的文件夹下
    for file in zip_file.namelist():
        zip_file.extract(file, dirname)
    zip_file.close()
    files = os.listdir(dirname)
    audio_path = ''
    text_path = ''
    for file in files:
        if os.path.splitext(file)[-1] in ['.mp3', '.wav']:
            audio_path = os.path.join(dirname, file)
        if os.path.splitext(file)[-1] == '.txt':
            text_path = os.path.join(dirname, file)
    return audio_path, text_path
