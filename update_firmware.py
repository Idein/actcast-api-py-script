# -*- coding: utf-8 -*-
from os import path
import sys
import time
import datetime
from actcast_api import ActcastAPI, Color, read_api_token

api_token_path = "./api_token"
page_limit = 100
request_interval_msec = 1000

def update_firmware(api, group_id, page_id=''):
    latest_info = api.get_firmware_info(group_id).items[0]

    release_date = api.iso8601toJST(latest_info.release_date)
    print('Latest firmware')
    print(f'firmware_type    : {latest_info.firmware_type}')
    print(f'firmware_version : {latest_info.firmware_version}')
    print(f'release_date     : {release_date}(JST)')
    print('=' * 50)


    next = ''
    page_start = 0
    
    # PageIDの指定があれば途中のページから始められるようにする
    if page_id != '':
        next = page_id
        page_start = (api.next2json(next)['offset'] // page_limit)

    ##################################################
    # デバイス総数と必要ページネーション回数を求める
    ##################################################
    params = {'limit':page_limit, 'next': next}
    data = api.get_devices_list(group_id, query_params=params)
    
    device_total = data.total
    page_end = (-1 * (-device_total // page_limit))  # 切り上げ

    print(f'device_total: {device_total}    page_limit:{page_limit}')
    print(f'execute: {page_start}-{page_end} page')
    print('=' * 80)
    print(f'Start. {datetime.datetime.now()}(JST)')

    ##################################################
    # ページネーション
    ##################################################
    for page in range(page_start, page_end):
        time.sleep(request_interval_msec/1000)

        print(f'\nPageID => {next}')

        params = {'limit':page_limit, 'next': next}
        data = api.get_devices_list(group_id, query_params=params)
        
        if data is False:
          print(Color.RED+'ERROR: Could not get device list.'+Color.COLOR_DEFAULT)
          sys.exit(1)

        # 1ページ分処理
        for i, item in enumerate(data.items, 1):
            index = (page * page_limit) + i

            # ファームウェアをアップデート
            device_id = item.device.id
            res = api.firmware_update(group_id, device_id)

            if res is False:
              print(Color.RED+f'└> ERROR: {device_id} {index:6d}/{device_total}')
              print('-' * 80, Color.COLOR_DEFAULT)
            else:
              print(f'{device_id} {index:6d}/{device_total}')

        if 'next' in data:
            next = data.next

    print('=' * 80)
    print(f'Done. {datetime.datetime.now()}(JST)')


if __name__ == '__main__':
  token = read_api_token(api_token_path)
  api = ActcastAPI(token)

  args = sys.argv
  if len(args) < 2:
    print("usage:")
    print(f"$ python3 {path.basename(__file__)} group_id [page_id]")
  elif len(args) == 2:
    group_id  = args[1]
    update_firmware(api, group_id)
  else:
    group_id  = args[1]
    page_id   = args[2]
    update_firmware(api, group_id, page_id)