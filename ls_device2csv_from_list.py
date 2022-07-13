# -*- coding: utf-8 -*-
from os import path
import sys
import time
import csv
import datetime
from actcast_api import ActcastAPI, Color, read_api_token

api_token_path = "./api_token"
request_interval_msec = 500

@ActcastAPI.api_request_exception
def get_device_info(api, group_id, device_id):
    endpoint = api.actcast.groups(group_id).devices(device_id)
    item = endpoint.get()

    return item

def ls_device2csv(api, group_id, id_list, out_path):
    index = 0

    with open(out_path, 'w', newline="") as out_f:
      writer = csv.writer(out_f)
      writer.writerow(['index', 'device_id', 'act.name', 'foundness', 'firmware_version'])

      with open(id_list) as id_list_f:
          for device_id in id_list_f:
            time.sleep(request_interval_msec/1000)

            index += 1
            device_id = device_id.rstrip()

            # デバイス情報抜き出し
            item = get_device_info(api, group_id, device_id)

            if item is False:
              print(Color.RED+f'└> ERROR: {device_id} {index:6d}')
              print('-' * 80, Color.COLOR_DEFAULT)
            else:
              print(f'{device_id} {index:6d}')
            
            device_id = item.device.id
            foundness = item.device.foundness
            act = item.device.act
            act_name = act.name if act is not None else "None"
            firmware_version = item.device.firmware_version
            writer.writerow([index, device_id, act_name, foundness, firmware_version])


    print('=' * 80)
    print(f'Done. {datetime.datetime.now()}(JST)')


if __name__ == '__main__':
  token = read_api_token(api_token_path)
  api = ActcastAPI(token)

  args = sys.argv
  if len(args) < 2:
    print("usage:")
    print(f"$ python3 {path.basename(__file__)} group_id id_list.txt output_path")
  else:
    group_id    = args[1]
    id_list     = args[2]
    output_path = args[3]
    ls_device2csv(api, group_id, id_list, output_path)