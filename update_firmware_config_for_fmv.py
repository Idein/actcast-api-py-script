# -*- coding: utf-8 -*-
import os
from os import path
import sys
import time
import datetime
import logging
import ast
from actcast_api import ActcastAPI, Color
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET

request_interval_msec = 500

ID_LIST_NAME = "device_list.txt"


def update_firmware_config_from_list(api, target_firmware_version):

    print_current_fw_info(api)

    update_fw_config(api, ID_LIST_NAME, target_firmware_version)

    logging.info('=' * 80)
    logging.info(f'Done. {datetime.datetime.now()}(JST)')


def update_fw_config(api, id_list_name, target_firmware_version):
    file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), id_list_name)
    with open(file_path) as f:
        while True:
            current_device_id = f.readline()
            if current_device_id == '':
                break

            update_single(api, current_device_id.rstrip(),
                          target_firmware_version)


def update_single(api, device_id, target_firmware_version):
    time.sleep(request_interval_msec / 1000)

    firmware_config = {"firmware_config": {
        "firmware_version": {
            "firmware_version": target_firmware_version,
            "type": "fixed"
        }
    }}

    item = api.set_device_settings(device_id, firmware_config)

    if item is False:
        logging.error(
            Color.RED + f'└> ERROR updating Firmware for device: {device_id}')
        logging.error('-' * 80, Color.COLOR_DEFAULT)
    else:
        logging.info(f'{device_id}')


def print_current_fw_info(api):
    latest_info = api.get_firmware_info().items[0]
    release_date = api.iso8601toJST(latest_info.release_date)
    logging.info('Latest firmware')
    logging.info(f'firmware_type    : {latest_info.firmware_type}')
    logging.info(f'firmware_version : {latest_info.firmware_version}')
    logging.info(f'release_date     : {release_date}(JST)')
    logging.info('=' * 50)
    logging.info(f'Start. {datetime.datetime.now()}(JST)')


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

    try:
        api = ActcastAPI()

        target_firmware_version = input("specify firmware version for firmware config: ")
        update_firmware_config_from_list(api, target_firmware_version)
    finally:
        input("Press any key to exit...")
