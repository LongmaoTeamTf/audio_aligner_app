"""
设置音量大小Models
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 15:21:11
@LastEditors: Wang Yao
@LastEditTime: 2019-11-17 15:39:06
"""
import os
from pydub import AudioSegment
from library.response.tfexception import TfException


def set_audio_volume(filepath, volume_size, output_path):
    """
    设置音量大小
    @param {type} filepath: 音频路径, volume_size: 分贝数, output_path: 输出路径
    @return: 无
    """
    if not os.path.exists(filepath):
        raise TfException(-1, 'No such file: '+filepath)
    audio = AudioSegment.from_file(filepath)
    audio += volume_size
    audio.export(output_path, format='wav')


def get_audio_params(filepath):
    """
    获取音频参数
    @param {type} filepath: 文件路径
    @return: 音频参数
    """
    if not os.path.exists(filepath):
        raise TfException(-1, 'No such file: '+filepath)
    params = {}
    audio = AudioSegment.from_file(filepath)
    params['channels'] = audio.channels
    params['framerate'] = audio.frame_rate
    params['duration'] = audio.duration_seconds
    return params
