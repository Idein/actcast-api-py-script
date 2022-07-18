# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
from actcast_api import ActcastAPI


def example(api, group_id, device_id):

    # QUERY PARAMETERS
    query_params = {
        'limit': 3,
        'next': '',
        'include_status': 0
    }

    # Request
    data = api.get_act_info_on_device(group_id, device_id)

    # Print result
    # actcast_api Wrapperの戻り値は正式なJSON形式で返ってこない(シングルクォーテーションが使われている)
    # なので、一旦辞書型にしてからjsonモジュールで扱う
    data = ast.literal_eval(str(data))
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    if len(args) < 3:
        print("usage:")
        print(f"$ python3 {os.path.basename(__file__)} group_id device_id")
    else:
        example(api, args[1], args[2])
