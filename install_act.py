# -*- coding: utf-8 -*-
from os import path
import sys
import time
from actcast_api import ActcastAPI, Color

page_limit = 100
request_interval_msec = 1000


def install_act(api, act_id, page_id=''):
    # Actの情報を得る
    act_info = api.get_act_info(act_id)
    print(f'Request install [ {act_id} : {act_info.name} ]')

    next = ''
    page_start = 0

    # PageIDの指定があれば途中のページから始められるようにする
    if page_id != '':
        next = page_id
        page_start = (api.next2json(next)['offset'] // page_limit)

    ##################################################
    # デバイス総数と必要ページネーション回数を求める
    ##################################################
    params = {'limit': page_limit, 'next': next}
    data = api.get_devices_list(query_params=params)

    device_total = data.total
    page_end = (-1 * (-device_total // page_limit))  # 切り上げ

    print(f'device_total: {device_total}    page_limit:{page_limit}')
    print(f'execute: {page_start}-{page_end} page')
    print('=' * 80)

    ##################################################
    # ページネーション
    ##################################################
    for page in range(page_start, page_end):
        time.sleep(request_interval_msec / 1000)

        print(f'\nPageID => {next}')

        params = {'limit': page_limit, 'next': next}
        data = api.get_devices_list(query_params=params)

        if data is False:
            print(Color.RED + 'ERROR: Could not get device list.' + Color.COLOR_DEFAULT)
            sys.exit(1)

        # 1ページ分処理
        for i, item in enumerate(data.items, 1):
            index = (page * page_limit) + i

            # actを追加
            device_id = item.device.id
            res = api.put_change_act(device_id, act_id, act_settings={})

            if res is False:
                print(
                    Color.RED + f'└> ERROR: {device_id} {index:6d}/{device_total}')
                print('-' * 80, Color.COLOR_DEFAULT)
            else:
                print(f'{device_id} {index:6d}/{device_total}')

        if 'next' in data:
            next = data.next

    print('=' * 80)
    print('Done.')


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    if len(args) < 2:
        print("usage:")
        print(f"$ python3 {path.basename(__file__)} act_id [page_id]")
    elif len(args) == 2:
        act_id = args[1]
        install_act(api, act_id)
    else:
        act_id = args[1]
        page_id = args[2]
        install_act(api, act_id, page_id)
