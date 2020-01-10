"""
工厂
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 21:30:06
@LastEditors: Wang Yao
@LastEditTime: 2019-11-18 11:49:14
"""
import sys
import logging
from os import makedirs
from os.path import dirname, exists
from flask import Flask
from cmreslogging.handlers import CMRESHandler
from config import settings
from library.database.tfmongo import TfMongo
from library.verification.token import TfToken



def create_app(config_path):
    """
    创建app
    @param config_path: 配置文件路径
    @return: app对象
    """
    app = Flask(settings.APP_NAME)
    app.config.from_pyfile(config_path)
    app.env = settings.APP_ENVIRONMENT
    app.static_folder = app.config['APP_STATIC_DIR']
    app.static_url_path = app.config['APP_STATIC_URL_PATH']
    for register in settings.APP_REGISTER:
        app.register_blueprint(register)

    with app.app_context():
        app.logger = create_logger(app)
        app.db = create_mongo(app)
        app.tk = create_token(app)

    return app


def create_mongo(app):
    """
    创建全局mongo
    @param app: app对象
    @return: 全局mongo对象
    """
    mongo_host = app.config['MONGO_HOST']
    mongo_port = app.config['MONGO_PORT']
    tfmongo = TfMongo(mongo_host, mongo_port)
    return tfmongo


def create_token(app):
    """
    创建token serializer
    @param app: app对象
    @return: 全局token serializer
    """
    token_secret_key = app.config['TOKEN_SECRET_KEY']
    token_expires_in = app.config['TOKEN_EXPIRES_IN']
    tftoken = TfToken(token_secret_key, token_expires_in)
    return tftoken


LOGGERS = {}
def create_logger(app, name=None):
    """
    创建全局logger
    @param app: app对象, name: logger名称
    @return: 全局logger
    """
    global LOGGERS

    if not name:
        name = __name__

    if LOGGERS.get(name):
        return LOGGERS.get(name)

    logger = logging.getLogger(name)
    logger.setLevel(app.config['LOG_LEVEL'])

    #输出日志到控制台
    if app.config['LOG_ENABLED'] and app.config['LOG_TO_CONSOLE']:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level=app.config['LOG_LEVEL'])
        formatter = logging.Formatter(app.config['LOG_FORMAT'])
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    #输出日志到文件
    if app.config['LOG_ENABLED'] and app.config['LOG_TO_FILE']:
        # 如果路径不存在，创建日志文件文件夹
        log_dir = dirname(app.config['APP_LOG_PATH'])
        if not exists(log_dir):
            makedirs(log_dir)
        # 添加 FileHandler
        file_handler = logging.FileHandler(app.config['APP_LOG_PATH'], encoding='utf-8')
        file_handler.setLevel(level=app.config['LOG_LEVEL'])
        formatter = logging.Formatter(app.config['LOG_FORMAT'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # #输出日志到elasticsearch
    # if app.config['LOG_ENABLED'] and app.config['LOG_TO_ES']:
    #
    #     # 添加 CMRESHandler
    #     es_handler = CMRESHandler(
    #         hosts=[{'host': app.config['ELASTIC_SEARCH_HOST'], 'port': app.config['ELASTIC_SEARCH_PORT']}],
    #         # 可以配置对应的认证权限
    #         auth_type=CMRESHandler.AuthType.NO_AUTH,
    #         es_index_name=app.config['ELASTIC_SEARCH_INDEX'],
    #         # 一个月分一个 Index
    #         index_name_frequency=CMRESHandler.IndexNameFrequency.MONTHLY,
    #         # 额外增加环境标识
    #         es_additional_fields={'environment': settings.APP_ENVIRONMENT}
    #     )
    #     es_handler.setLevel(level=app.config['LOG_LEVEL'])
    #     formatter = logging.Formatter(app.config['LOG_FORMAT'])
    #     es_handler.setFormatter(formatter)
    #     logger.addHandler(es_handler)

    #保存到全局loggers
    LOGGERS[name] = logger
    return logger
