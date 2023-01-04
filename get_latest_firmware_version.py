# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
from actcast_api import ActcastAPI


def get_latest_firmware_version(api):

    # Request
    data = api.get_latest_firmware_version()

    # Print result
    # actcast_api Wrapperの戻り値は正式なJSON形式で返ってこない(シングルクォーテーションが使われている)
    # なので、一旦辞書型にしてからjsonモジュールで扱う
    data = ast.literal_eval(str(data))
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    api = ActcastAPI()

    get_latest_firmware_version(api)
