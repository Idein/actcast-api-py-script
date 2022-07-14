# -*- coding: utf-8 -*-
from os import path
import sys
import time
import datetime
from actcast_api import ActcastAPI, Color

request_interval_msec = 500

class CurrentInfo:
  last_update_start_time = datetime.datetime.now()
  update_batch_cnt = 0

class Setting:
  update_with_interval = False
  update_interval = 0
  devices_per_interval = 10000


def update_firmware(api, group_id, id_list_name):
  init_interval_settings(api)

  print_latest_fw_info(api, group_id)

  update_fw(api, group_id, id_list_name)

  print('=' * 80)
  print(f'Done. {datetime.datetime.now()}(JST)')

def init_interval_settings(api):
  # SBプロジェクト対応。一定時間内に更新するデバイス数を制限する
  if 'update_firmware_interval' in api.setting_json and 'update_firmware_devices_per_interval' in api.setting_json:
    Setting.update_with_interval = True
    Setting.update_interval = api.setting_json['update_firmware_interval']
    Setting.devices_per_interval = api.setting_json['update_firmware_devices_per_interval']

def update_fw(api, group_id, id_list_name):

  with open(id_list_name) as f:
    while True:
      current_device_id = f.readline()
      if current_device_id == '':
        break

      update_single(api, group_id, current_device_id.rstrip())

      if Setting.update_with_interval: 
        sleep_in_interval()

def  sleep_in_interval():
  CurrentInfo.update_batch_cnt += 1
  if CurrentInfo.update_batch_cnt >= Setting.devices_per_interval:
    CurrentInfo.update_batch_cnt = 0
    current_time = datetime.datetime.now()
    # update_intervalの秒数 - すでにこれまでの更新処理で利用した秒数 だけsleepする
    time.sleep(Setting.update_interval - (current_time - CurrentInfo.last_update_start_time).seconds)
    CurrentInfo.last_update_start_time = datetime.datetime.now()


def update_single(api, group_id, device_id):
  time.sleep(request_interval_msec/1000)

  item = api.firmware_update(group_id, device_id)

  if item is False:
    print(Color.RED+f'└> ERROR updating Firmware for device: {device_id}')
    print('-' * 80, Color.COLOR_DEFAULT)
  else:
    print(f'{device_id}')

def print_latest_fw_info(api, group_id):
  latest_info = api.get_firmware_info(group_id).items[0]
  release_date = api.iso8601toJST(latest_info.release_date)
  print('Latest firmware')
  print(f'firmware_type    : {latest_info.firmware_type}')
  print(f'firmware_version : {latest_info.firmware_version}')
  print(f'release_date     : {release_date}(JST)')
  print('=' * 50)
  print(f'Start. {datetime.datetime.now()}(JST)')


if __name__ == '__main__':
  api = ActcastAPI()

  args = sys.argv
  if len(args) < 2:
    print("usage:")
    print(f"$ python3 {path.basename(__file__)} group_id id_list.txt")
  else:
    group_id  = args[1]
    id_list_name   = args[2]
    update_firmware(api, group_id, id_list_name)