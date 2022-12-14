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

request_interval_msec = 1000


class DeviceSpecificSettingsAction(Enum):
    RESTORE = 'RESTORE'
    USE_DEFAULT = 'USE_DEFAULT'
    USE_LOCAL = 'USE_LOCAL'
    USE_LOCAL_REPLACE_PARTIAL = 'USE_LOCAL_REPLACE_PARTIAL'
    FORCED_RESTORE = 'FORCED_RESTORE'

    @classmethod
    def value_of(cls, target_value):
        for e in DeviceSpecificSettingsAction:
            if e.value == target_value:
                return e
        return DeviceSpecificSettingsAction.RESTORE


class CurrentInfo:
    act_info = ''
    last_update_start_time = datetime.datetime.now()
    update_batch_cnt = 0


class Setting:
    update_with_interval = False
    update_interval = 0
    devices_per_interval = 10000
    device_specific_settings_action = DeviceSpecificSettingsAction.RESTORE
    enable_rand_maximum_timelimit_minute_for_sb = False
    replace_items = []


def init_interval_settings(api):
    # SBプロジェクト対応。一定時間内に更新するデバイス数を制限する
    if 'update_interval' in api.setting_json and 'update_devices_per_interval' in api.setting_json:
        Setting.update_with_interval = True
        Setting.update_interval = api.setting_json['update_interval']
        Setting.devices_per_interval = api.setting_json['update_devices_per_interval']
    if 'install_act_settings_from_file' in api.setting_json:
        Setting.install_act_settings_from_file = api.setting_json['install_act_settings_from_file']
    if 'device_specific_settings_action' in api.setting_json:
        Setting.device_specific_settings_action = DeviceSpecificSettingsAction.value_of(
            api.setting_json['device_specific_settings_action'])
    if 'enable_rand_maximum_timelimit_minute_for_sb' in api.setting_json:
        Setting.enable_rand_maximum_timelimit_minute_for_sb = api.setting_json[
            'enable_rand_maximum_timelimit_minute_for_sb']
    if 'replace_items' in api.setting_json:
        Setting.replace_items = api.setting_json['replace_items']


def install_act_from_list(api, act_id, id_list_name):
    init_interval_settings(api)

    # インストールするActの情報を得る
    CurrentInfo.act_info = api.get_act_info(act_id)

    print(
        f'Request to install Act: [ {act_id} : {CurrentInfo.act_info.name} ]')
    print(f'target devices total: {sum([1 for _ in open(id_list_name)])}')
    print('=' * 80)

    install_act(api, act_id, id_list_name)

    print('=' * 80)
    print('Done.')


def install_act(api, act_id, id_list_name):
    with open(id_list_name) as f:
        while True:
            current_device_id = f.readline().rstrip()
            if current_device_id == '':
                break

            if Setting.update_with_interval:
                sleep_in_interval()

            install_single(api, act_id, current_device_id)


def sleep_in_interval():
    CurrentInfo.update_batch_cnt += 1
    if CurrentInfo.update_batch_cnt > Setting.devices_per_interval:
        CurrentInfo.update_batch_cnt = 0
        current_time = datetime.datetime.now()
        # {update_intervalの秒数 - すでにこれまでの更新処理で利用した秒数} だけsleepする
        if (Setting.update_interval > (current_time - CurrentInfo.last_update_start_time).seconds):
            time.sleep(Setting.update_interval - (current_time -
                       CurrentInfo.last_update_start_time).seconds)
        CurrentInfo.last_update_start_time = datetime.datetime.now()


def install_single(api, act_id, current_device_id):
    time.sleep(request_interval_msec / 1000)

    act_settings = get_act_settings(api, current_device_id)

    # 各プロジェクト向け特殊対応
    # 一部設定値を任意の値に書き換えて送信する
    act_settings = replace_partial_settings(api, current_device_id, act_settings)

    res = api.put_change_act(current_device_id, act_id, act_settings)

    if res is False:
        print(Color.RED + f'└> ERROR: {current_device_id}')
        print('-' * 80, Color.COLOR_DEFAULT)
    else:
        print(f'{current_device_id}' 'install success')


def replace_partial_settings(api, current_device_id, act_settings):
    # SBプロジェクト用特殊対応
    # Speaker Separation in CounterアプリのDevice Spefic Settingの中の、
    # maximum_timelimit_minuteの値を0~59でランダムで書き換える
    if Setting.enable_rand_maximum_timelimit_minute_for_sb:
        act_settings['maximum_timelimit_minute'] = random.randint(0, 59)

    # ファミマプロジェクト特殊対応
    # 通常解像度→高解像度カメラ入れ替えのため、Setting Schemaが異なる新アプリに入れ替えが必要だが、
    # カメラの閾値設定は前回のものを引き継ぎたい、という要望への対応。
    # 基本はローカルのact_setting.jsonの設定を利用するが、
    # replace_partial_itemsに指定した設定値を既存のDevice Specific Settingから取得したものと置き換える
    if Setting.device_specific_settings_action == DeviceSpecificSettingsAction.USE_LOCAL_REPLACE_PARTIAL:
        current_act_info = api.get_act_info_on_device(current_device_id)
        current_act_info = ast.literal_eval(str(current_act_info))
        currect_act_settings = current_act_info['settings']
        for replace_item in Setting.replace_items:
            act_settings[replace_item] = currect_act_settings[replace_item]

    return act_settings


def get_act_settings(api, current_device_id):
    match Setting.device_specific_settings_action:
        case DeviceSpecificSettingsAction.RESTORE | DeviceSpecificSettingsAction.FORCED_RESTORE:
            current_act_info = api.get_act_info_on_device(current_device_id)
            # actcast_api Wrapperの戻り値は正式なJSON形式で返ってこない(シングルクォーテーションが使われている)
            # なので、一旦辞書型にしてからjsonモジュールで扱う
            current_act_info = ast.literal_eval(str(current_act_info))
            # ・release_idが同じactをインストールするとき
            # ・setting.jsonでFORCED_RESTOREが指定されているとき
            # のいずれかの条件のとき、前回の設定をリストアする
            # ※FORCED_RESTOREの場合、Settingのスキーマが異なるActをインストールしようとするとエラーとなるので注意
            if ((CurrentInfo.act_info['release_id'] == current_act_info['release_id'])
                    or (Setting.device_specific_settings_action == DeviceSpecificSettingsAction.FORCED_RESTORE)):
                return current_act_info['settings']
            else:
                return {}
        case DeviceSpecificSettingsAction.USE_LOCAL | DeviceSpecificSettingsAction.USE_LOCAL_REPLACE_PARTIAL:
            # ローカルのact_settings.jsonファイルから設定を反映する
            return get_act_settings_from_file()
        case DeviceSpecificSettingsAction.USE_DEFAULT:
            # Actのデフォルト設定を利用する
            return {}
        case _:
            return {}


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

    if len(args) < 3:
        print("usage:")
        print(
            f"$ python3 {path.basename(__file__)} act_id id_list.txt")
    else:
        act_id = args[1]
        id_list_name = args[2]
        install_act_from_list(api, act_id, id_list_name)
