# -*- coding: utf-8 -*-
from os import path
import sys
from actcast_api import ActcastAPI, Color


def check_firmware(api):
    latest_info = api.get_firmware_info().items[0]

    release_date = api.iso8601toJST(latest_info.release_date)
    print('Latest firmware')
    print(f'firmware_type    : {latest_info.firmware_type}')
    print(f'firmware_version : {latest_info.firmware_version}')
    print(f'release_date     : {release_date}(JST)')

    print('=' * 80)
    print('Done.')


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    check_firmware(api)
