# -*- coding: utf-8 -*-
import os
from os import path
import sys
import time
import datetime
import logging
from actcast_api import ActcastAPI, Color
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET

request_interval_msec = 1


class CurrentInfo:
    last_update_start_time = datetime.datetime.now()
    update_batch_cnt = 0


class Setting:
    update_with_interval = False
    update_interval = 0
    devices_per_interval = 10000


def update_firmware(api, id_list_name):
    init_interval_settings(api)

    group_id = api.setting_json['group_id']
    print_latest_fw_info(api, group_id)

    update_fw(api, id_list_name)

    logging.info('=' * 80)
    logging.info(f'Done. {datetime.datetime.now()}(JST)')


def init_interval_settings(api):
    # SBプロジェクト対応。一定時間内に更新するデバイス数を制限する
    if 'update_interval' in api.setting_json and 'update_devices_per_interval' in api.setting_json:
        Setting.update_with_interval = True
        Setting.update_interval = api.setting_json['update_interval']
        Setting.devices_per_interval = api.setting_json['update_devices_per_interval']


def update_fw(api, id_list_name):
    with open(id_list_name) as f:
        while True:
            current_device_id = f.readline()
            if current_device_id == '':
                break

            update_single(api, current_device_id.rstrip())

            if Setting.update_with_interval:
                sleep_in_interval()


def sleep_in_interval():
    CurrentInfo.update_batch_cnt += 1
    if CurrentInfo.update_batch_cnt >= Setting.devices_per_interval:
        CurrentInfo.update_batch_cnt = 0
        current_time = datetime.datetime.now()
        # update_intervalの秒数 - すでにこれまでの更新処理で利用した秒数 だけsleepする
        if (Setting.update_interval >= (current_time - CurrentInfo.last_update_start_time).seconds):
            time.sleep(Setting.update_interval - (current_time - CurrentInfo.last_update_start_time).seconds)
            CurrentInfo.last_update_start_time = datetime.datetime.now()


def update_single(api, device_id):
    time.sleep(request_interval_msec / 1000)

    item = api.firmware_update(device_id)

    if item is False:
        logging.error(
            Color.RED + f'└> ERROR updating Firmware for device: {device_id}')
        logging.error('-' * 80, Color.COLOR_DEFAULT)
    else:
        logging.info(f'{device_id}')


def print_latest_fw_info(api, group_id):
    latest_info = api.get_firmware_info(group_id).items[0]
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

    api = ActcastAPI()

    args = sys.argv
    if len(args) < 1:
        logging.info("usage:")
        logging.info(
            f"$ python3 {path.basename(__file__)} id_list.txt")
    else:
        id_list_name = args[1]
        update_firmware(api, id_list_name)
