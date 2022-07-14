# -*- coding: utf-8 -*-
from os import path
import sys
import time
import csv
from actcast_api import ActcastAPI, Color

page_limit = 100
request_interval_msec = 1000

def ls_device2csv(api, group_id, out_path, page_id=''):
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


    with open(out_path, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'device_id', 'foundness', 'firmware_version'])

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

                firmware_version = item.device.firmware_version
                foundness = item.device.foundness
                device_id = item.device.id

                writer.writerow([index, device_id, foundness, firmware_version])
                print(f'{device_id} {index:6d}/{device_total}')

            if 'next' in data:
                next = data.next

    print('=' * 80)
    print('Done.')


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    if len(args) < 3:
        print("usage:")
        print(f"$ python3 {path.basename(__file__)} group_id output_path [page_id]")
    elif len(args) == 3:
        group_id    = args[1]
        output_path = args[2]
        ls_device2csv(api, group_id, output_path)
    else:
        group_id    = args[1]
        output_path = args[2]
        page_id     = args[3]
        ls_device2csv(api, group_id, output_path, page_id)