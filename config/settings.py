import os
from modules.voice_manager.volume.controller.index import GROUP_VOLUME
from modules.audio_aligner.controller.index import GROUP_ALIGNER


APP_CONFIG_MAP = {
    "development": "dev_config.py",
    "production": "pro_config.py"
}


APP_ENVIRONMENT = 'production'
APP_NAME = 'audio_manager_api - ' + APP_ENVIRONMENT
APP_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_CONFIG_PATH = os.path.join(APP_BASE_DIR, 'config', APP_CONFIG_MAP[APP_ENVIRONMENT])
APP_HOST = '0.0.0.0'
APP_PORT = 8100
APP_DEBUG = True


APP_REGISTER = {
    GROUP_VOLUME,
    GROUP_ALIGNER
}