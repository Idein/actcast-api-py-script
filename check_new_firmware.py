# -*- coding: utf-8 -*-
from os import path
import sys
from actcast_api import ActcastAPI, Color, read_api_token

api_token_path = "./api_token"

def check_firmware(api, group_id):
    latest_info = api.get_firmware_info(group_id).items[0]

    release_date = api.iso8601toJST(latest_info.release_date)
    print('Latest firmware')
    print(f'firmware_type    : {latest_info.firmware_type}')
    print(f'firmware_version : {latest_info.firmware_version}')
    print(f'release_date     : {release_date}(JST)')

    print('=' * 80)
    print('Done.')


if __name__ == '__main__':
    token = read_api_token(api_token_path)
    api = ActcastAPI(token)

    args = sys.argv
    if len(args) < 2:
        print("usage:")
        print(f"$ python3 {path.basename(__file__)} group_id")
    else:
        group_id    = args[1]
        check_firmware(api, group_id)