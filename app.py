"""
app入口
@version: v1.0.1
@Company: Thefair
@Author: Wang Yao
@Date: 2019-11-17 21:26:28
@LastEditors: Wang Yao
@LastEditTime: 2019-11-18 11:43:49
"""
import os
from flask import send_from_directory, request, send_file
from flask import render_template
from config import settings, pro_config
from factory import create_app


ENV_APP_PATH = os.path.join(os.path.dirname(__file__), 'app.py')
os.environ['FLASK_APP'] = ENV_APP_PATH


app = create_app(settings.APP_CONFIG_PATH)
app.app_context().push()

if not os.path.exists(pro_config.APP_UPLOAD_PATH):
    os.makedirs(pro_config.APP_UPLOAD_PATH)

if not os.path.exists(pro_config.APP_VOLUME_PATH):
    os.makedirs(pro_config.APP_VOLUME_PATH)


@app.route('/public_resource/<path:filename>')
@app.route('/static/js/<path:filename>')
@app.route('/static/css/<path:filename>')
def serve_static(filename):
    """
    获取静态资源
    @param {get} filename: 文件名
    @return: 静态资源文件
    """

    root_dir = pro_config.APP_STATIC_DIR

    if request.path.startswith("/static/"):
        file_path = os.path.join(root_dir, "fe", "build", request.path.strip("/"))
        return send_file(file_path)

    return send_from_directory(root_dir, filename)


@app.route('/page/changeVolume')
@app.route('/page/chineseAligner')
def serve_static_html():
    """
    请求音量设置大小页面
    @return: 音量设置大小页面
    """
    app.template_folder = pro_config.APP_HTML_STATIC_DIR
    return render_template('index.html')


if __name__ == "__main__":
    app.run(
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        debug=settings.APP_DEBUG
    )
