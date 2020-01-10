"""
工具函数
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-11-01 17:07
# @Site    :
# @File    : tools.py
# @Software: PyCharm


from pydub import AudioSegment


def mp3_to_wav(mp3_path, wav_path):
    """
    MP3转wav
    :param mp3_path:
    :param wav_path:
    :return:
    """
    sound = AudioSegment.from_mp3(mp3_path)
    sound = sound.set_frame_rate(16000).set_channels(1)
    sound.export(wav_path, format='wav', codec='pcm_s16le')
