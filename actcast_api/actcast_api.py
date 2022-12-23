# -*- coding: utf-8 -*-
import os
import sys
import tortilla
import base64
import json
import logging
import pprint
from datetime import datetime, timezone, timedelta
from requests.exceptions import RequestException
import time


class Color:
    BLACK = '\033[30m'  # (文字)黒
    RED = '\033[31m'  # (文字)赤
    GREEN = '\033[32m'  # (文字)緑
    YELLOW = '\033[33m'  # (文字)黄
    BLUE = '\033[34m'  # (文字)青
    MAGENTA = '\033[35m'  # (文字)マゼンタ
    CYAN = '\033[36m'  # (文字)シアン
    WHITE = '\033[37m'  # (文字)白
    COLOR_DEFAULT = '\033[39m'  # 文字色をデフォルトに戻す
    BOLD = '\033[1m'   # 太字
    UNDERLINE = '\033[4m'   # 下線
    INVISIBLE = '\033[08m'  # 不可視
    RESET = '\033[0m'   # 全てリセット

#############################
# Actcast API Wrapper
#############################


class ActcastAPI:

    def __init__(self):
        SETTING_JSON_PATH = './setting.json'
        if not os.path.isfile(SETTING_JSON_PATH):
            print(f"{SETTING_JSON_PATH} に[setting.json]ファイルがありません。")
            sys.exit(1)
        with open(SETTING_JSON_PATH) as f:
            self.setting_json = json.load(f)

        self.actcast = tortilla.wrap('https://api.actcast.io/v0/')
        if not 'api_token' in self.setting_json:
            print("setting.jsonファイル内にapi_tokenの項目がありません。")
            sys.exit(1)
        self.actcast.config.headers.Authorization = 'token ' + \
            self.setting_json['api_token']

        if 'max_retry' in self.setting_json:
            self.MAX_RETRY = self.setting_json['max_retry']
        else:
            self.MAX_RETRY = 5

    def isJsonFormat(self, line):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            return False
        except ValueError as e:
            return False
        except Exception as e:
            return False
        return True

    def iso8601toJST(self, datetime_str):
        try:
            timestamp = datetime.strptime(
                datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        except ValueError as e:
            timestamp = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')
        timestamp = timestamp.astimezone(timezone(timedelta(hours=+9)))
        timestamp = timestamp.strftime('%Y/%m/%d %H:%M:%S')
        return timestamp

    def next2json(self, base64str):
        str = base64.b64decode(base64str).decode()
        return json.loads(str)

    # エラーチェックデコレータ

    def api_request_exception(func):
        def wrapper(self, *args, **kwargs):
            for i in range(self.MAX_RETRY):
                try:
                    return func(self, *args, **kwargs)

                # HTTP error
                except RequestException as e:
                    print(Color.RED, end='')
                    print(f'Request failed: {func.__name__}()\n')
                    print(f"Executing {e.request.method} request")
                    print(f"URL: {e.request.url}\n")

                    print(f"Got {e.response.status_code} {e.response.reason}")
                    print(e)

                    if self.isJsonFormat(e.response.text):
                        message = json.loads(e.response.text)
                        print(json.dumps(message, indent=2))
                    else:
                        print(e.response.text)

                    print(Color.COLOR_DEFAULT, end='')
                    # sys.exit(1)

                # args error
                except ValueError as e:
                    print(Color.RED, end='')
                    print(f'ValueError: {func.__name__}()')
                    print(e)
                    print(Color.YELLOW, end='')
                    print('note: The args may be incorrect...')
                    print(Color.COLOR_DEFAULT, end='')
                    # sys.exit(1)

                print(f'リクエストリトライ{i+1}')
                time.sleep(1)

            return False

        return wrapper

    # デバイス一覧
    @api_request_exception
    def get_devices_list(self, groupid, query_params=""):
        endpoint = self.actcast.groups(groupid).devices
        res = endpoint.get(params=query_params)

        return res

    # デバイス情報の取得
    def get_device_info(self, groupid, deviceid, query_params=""):
        endpoint = self.actcast.groups(groupid).devices(deviceid)
        res = endpoint.get(params=query_params)

        return res

    # デバイス上の設定変更
    def set_device_settings(self, groupid, deviceid, device_settings):
        endpoint = self.actcast.groups(groupid).devices(deviceid)
        res = endpoint.patch(json=device_settings)

        return res

    # Act情報の取得
    @api_request_exception
    def get_act_info(self, group_id, act_id):
        endpoint = self.actcast.groups(group_id).acts(act_id)
        res = endpoint.get()

        return res

    # 特定デバイスにインストールされたAct情報の取得
    @api_request_exception
    def get_act_info_on_device(self, group_id, device_id):
        endpoint = self.actcast.groups(group_id).devices(device_id).act
        res = endpoint.get()

        return res

    # デバイス上のActの変更
    @api_request_exception
    def put_change_act(self, group_id, device_id, act_id, act_settings):
        payload = {"id": int(act_id), "settings": act_settings}

        endpoint = self.actcast.groups(group_id).devices(device_id).act
        res = endpoint.put(json=payload)

        return res

    # デバイスにジョブコマンドを送信
    @api_request_exception
    def post_job_command(self, group_id, device_id, job_command_type):
        endpoint = self.actcast.groups(group_id).devices(
            device_id).jobs(job_command_type)
        res = endpoint.post()

        return res

    # ファームウェアアップデート
    @api_request_exception
    def firmware_update(self, group_id, device_id):
        job_command_type = "firmware_update"
        res = self.post_job_command(group_id, device_id, job_command_type)

        return res

    # デバイスステータスの更新
    @api_request_exception
    def status_reload(self, group_id, device_id):
        job_command_type = "device_status"
        res = self.post_job_command(group_id, device_id, job_command_type)

        return res

    # デバイス上のAct削除
    @api_request_exception
    def del_act(self, groupid, deviceid):
        endpoint = self.actcast.groups(groupid).devices(deviceid).act
        res = endpoint.delete()

        return res

    # イベントログ取得
    @api_request_exception
    def get_event_log(self, groupid, deviceid, query_params=""):
        endpoint = self.actcast.groups(groupid).devices(deviceid).event_logs
        res = endpoint.get(params=query_params)

        return res

    # Actログ取得
    @api_request_exception
    def get_act_log(self, groupid, deviceid, query_params=""):
        endpoint = self.actcast.groups(groupid).devices(deviceid).act_logs
        res = endpoint.get(params=query_params)

        return res

    # ファームウェア詳細
    @api_request_exception
    def get_firmware_info(self, group_id, query_params=""):
        endpoint = self.actcast.groups(group_id).firmwares
        res = endpoint.get(params=query_params)

        return res

    # 最新FW Ver取得
    @api_request_exception
    def get_latest_firmware_version(self, group_id, query_params=""):
        endpoint = self.actcast.groups(group_id).firmwares.raspberrypi.versions
        res = endpoint.get(params=query_params)

        return res


if __name__ == '__main__':
    api = ActcastAPI()

    res = api.get_firmware_info(707)
    print(res.items[0].firmware_version)
