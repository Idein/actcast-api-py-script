# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
from actcast_api import ActcastAPI


def example(api, id):
    # PATH PARAMETERS
    group_id = id

    # QUERY PARAMETERS
    query_params = {
        'limit': 3,
        'include_status': 0
    }

    #test = api.get_act_log(group_id, '7f616dfd-6e43-4547-8f40-75af40bb4957')
    test = api.get_firmware_info(group_id)
    firmware_info = api.get_firmware_info(group_id).items[0]
    # print('what is inside test?{}', test)
    print(firmware_info.firmware_version)

    # Request
    #data = api.get_devices_list(group_id, query_params)

    # Print result
    # actcast_api Wrapperの戻り値は正式なJSON形式で返ってこない(シングルクォーテーションが使われている)
    # なので、一旦辞書型にしてからjsonモジュールで扱う
    #data = ast.literal_eval(str(data))
    #print(json.dumps(data, indent=2))


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    if len(args) < 2:
        print("usage:")
        print(f"$ python3 {os.path.basename(__file__)} group_id")
    else:
        example(api, args[1])
