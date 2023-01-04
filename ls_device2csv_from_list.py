# -*- coding: utf-8 -*-
from os import path
import sys
import time
import csv
import datetime
from actcast_api import ActcastAPI, Color

request_interval_msec = 500


def ls_device2csv(api, id_list, out_path):
    index = 0

    with open(out_path, 'w', newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(['index', 'device_id', 'act.name',
                        'foundness', 'firmware_version'])

        with open(id_list) as id_list_f:
            for device_id in id_list_f:
                time.sleep(request_interval_msec / 1000)

                index += 1
                device_id = device_id.rstrip()

                # デバイス情報抜き出し
                item = api.get_device_info(api, device_id)

                if item is False:
                    print(Color.RED + f'└> ERROR: {device_id} {index:6d}')
                    print('-' * 80, Color.COLOR_DEFAULT)
                else:
                    print(f'{device_id} {index:6d}')

                device_id = item.device.id
                foundness = item.device.foundness
                act = item.device.act
                act_name = act.name if act is not None else "None"
                firmware_version = item.device.firmware_version
                writer.writerow([index, device_id, act_name,
                                foundness, firmware_version])

    print('=' * 80)
    print(f'Done. {datetime.datetime.now()}(JST)')


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    if len(args) < 2:
        print("usage:")
        print(
            f"$ python3 {path.basename(__file__)} id_list.txt output_path")
    else:
        id_list = args[1]
        output_path = args[2]
        ls_device2csv(api, id_list, output_path)
