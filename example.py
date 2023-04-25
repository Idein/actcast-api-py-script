# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
from actcast_api import ActcastAPI


def example(api):

    # QUERY PARAMETERS
    query_params = {
        'limit': 3,
        'include_status': 0
    }

    firmware_info = api.get_firmware_info().items[0]
    print(firmware_info.firmware_version)

    # Request
    data = api.get_devices_list(query_params)

    # Print result
    # actcast_api Wrapperの戻り値は正式なJSON形式で返ってこない(シングルクォーテーションが使われている)
    # なので、一旦辞書型にしてからjsonモジュールで扱う
    data = ast.literal_eval(str(data))
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    example(api)
