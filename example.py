# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
from actcast_api import ActcastAPI, read_api_token

api_token_path = "./api_token"


def example(api, id):
    # PATH PARAMETERS
    group_id = id

    # QUERY PARAMETERS
    query_params = {
        'limit': 3,
        'next': '',
        'include_status': 0
    }

    # Request
    data = api.get_devices_list(group_id, query_params)

    # Print result
    # actcast_api Wrapperの戻り値は正式なJSON形式で返ってこない(シングルクォーテーションが使われている)
    # なので、一旦辞書型にしてからjsonモジュールで扱う
    data = ast.literal_eval(str(data))
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    token = read_api_token(api_token_path)
    api = ActcastAPI(token)

    args = sys.argv
    if len(args) < 2:
        print("usage:")
        print(f"$ python3 {os.path.basename(__file__)} group_id")
    else:
        example(api, args[1])
