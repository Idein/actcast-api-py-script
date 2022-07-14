# -*- coding: utf-8 -*-
from os import path
import sys
import time
import datetime
from actcast_api import ActcastAPI, Color

request_interval_msec = 500

def update_firmware(api, group_id, id_list):
    latest_info = api.get_firmware_info(group_id).items[0]

    release_date = api.iso8601toJST(latest_info.release_date)
    print('Latest firmware')
    print(f'firmware_type    : {latest_info.firmware_type}')
    print(f'firmware_version : {latest_info.firmware_version}')
    print(f'release_date     : {release_date}(JST)')
    print('=' * 50)
    print(f'Start. {datetime.datetime.now()}(JST)')

    index = 0
    with open(id_list) as f:
        for device_id in f:
          time.sleep(request_interval_msec/1000)

          index += 1
          device_id = device_id.rstrip()

          # ファームウェアをアップデート
          item = api.firmware_update(group_id, device_id)

          if item is False:
            print(Color.RED+f'└> ERROR: {device_id} {index:6d}')
            print('-' * 80, Color.COLOR_DEFAULT)
          else:
            print(f'{device_id} {index:6d}')


    print('=' * 80)
    print(f'Done. {datetime.datetime.now()}(JST)')


if __name__ == '__main__':
  api = ActcastAPI()

  args = sys.argv
  if len(args) < 2:
    print("usage:")
    print(f"$ python3 {path.basename(__file__)} group_id id_list.txt")
  else:
    group_id  = args[1]
    id_list   = args[2]
    update_firmware(api, group_id, id_list)