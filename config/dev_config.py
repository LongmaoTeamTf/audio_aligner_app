import os

# APP STATIC config
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_STATIC_DIR = os.path.join(APP_PATH, "static")
APP_LOG_PATH = os.path.join(APP_PATH, 'logs', 'app.log')
APP_STATIC_URL_PATH = '/public_resource'
# LOG config
LOG_ENABLED = True  # 是否开启日志
LOG_TO_CONSOLE = True  # 是否输出到控制台
LOG_TO_FILE = True  # 是否输出到文件
LOG_TO_ES = False  # 是否输出到es
LOG_LEVEL = 'DEBUG'  # 日志级别
LOG_FORMAT = '%(levelname)s - %(asctime)s - process: %(process)d - %(filename)s - %(name)s - %(lineno)d - %(module)s - %(message)s'  # 每条日志输出格式
# ES config
# ELASTIC_SEARCH_HOST = 'localhost'  # es集群的名字 elasticsearch host
# ELASTIC_SEARCH_PORT = 9200  # es运行的端口
# ELASTIC_SEARCH_INDEX = 'runtime'  # es索引的名字
# TOKEN config
TOKEN_SECRET_KEY = os.urandom(24)
TOKEN_EXPIRES_IN = 86400
# DB config
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
# volume config
APP_UPLOAD_PATH = os.path.join(APP_STATIC_DIR, 'upload')
APP_VOLUME_PATH = os.path.join(APP_STATIC_DIR, 'volume')
APP_STATIC_URL_UPLOAD_PATH = os.path.join(APP_STATIC_URL_PATH, 'upload')
APP_STATIC_URL_VOLUME_PATH = os.path.join(APP_STATIC_URL_PATH, 'volume')
# kaldi path
KALDI_BASE = '/media/xddz/xddz/code/kaldi-trunk'
ENGLIST_KALDI_PATH = KALDI_BASE + '/egs/librispeech/s5'
CHINESE_KALDI_PATH = KALDI_BASE + '/egs/aidatatang_200zh/s5'
