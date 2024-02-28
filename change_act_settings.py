# -*- coding: utf-8 -*-
from difflib import restore
import os
from os import path
import sys
import ast
import time
import datetime
import logging
import json
import random
from enum import Enum
from traitlets import Bool, default
from actcast_api import ActcastAPI, Color
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET


def change_act_settings(api, device_id):

    act_settings = get_act_settings_from_file()

    res = api.change_act_settings(device_id, act_settings)

    if res is False:
        print(Color.RED + f'└> ERROR: {device_id}')
        print('-' * 80, Color.COLOR_DEFAULT)
    else:
        print(f'{device_id}' 'act setting change success')


def get_act_settings_from_file():
    ACT_SETTING_JSON_PATH = './act_settings.json'
    if not os.path.isfile(ACT_SETTING_JSON_PATH):
        print(f"{ACT_SETTING_JSON_PATH} に[act_settings.json]ファイルがありません。")
        sys.exit(1)
    with open(ACT_SETTING_JSON_PATH) as f:
        return json.load(f)


if __name__ == '__main__':
    # ログ出力用ストリームハンドラの設定
    stream_handler = StreamHandler()
    stream_handler.setLevel(INFO)
    stream_handler.setFormatter(Formatter("%(message)s"))

    # ログファイル保存先の有無チェック
    if not os.path.isdir('./Log'):
        os.makedirs('./Log', exist_ok=True)

    # ファイルハンドラの設定
    file_handler = FileHandler(
        f"./Log/update_firmware_from_list_{datetime.datetime.now():%Y%m%d%H%M%S}.log"
    )
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
    )
    logging.basicConfig(level=NOTSET, handlers=[stream_handler, file_handler])

    api = ActcastAPI()

    args = sys.argv

    if len(args) < 2:
        print("usage:")
        print(
            f"$ python3 {path.basename(__file__)} device_id")
    else:
        device_id = args[1]
        change_act_settings(api, device_id)
