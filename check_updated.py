# -*- coding: utf-8 -*-
from os import path
import sys
import time
from datetime import datetime, timezone, timedelta
from actcast_api import ActcastAPI

request_interval_msec = 1000


def update_firmware(api):
    next = ""
    while True:
        time.sleep(request_interval_msec / 1000)

        # params = {'next': next}
        params = {}
        data = api.get_devices_list(query_params=params)

        for item in data.items:
            device_id = item.device.id

            print('=' * 80)
            print(f'device_id : {device_id}')

            logs = api.get_event_log(device_id)

            test = api.get_act_log(device_id)
            print('what is inside next?{}', test.next)
            for log in logs.items:
                if 'firmware_updated' in log.event.type:
                    timestamp = api.iso8601toJST(log.timestamp)
                    print(
                        f"\033[33m{timestamp} {log.event.type:20s} {log.description}\033[39m")

                if 'firmware_updating' in log.event.type:
                    timestamp = api.iso8601toJST(log.timestamp)
                    print(
                        f"\033[33m{timestamp} {log.event.type:20s} {log.description}\033[39m")
                    break

            print('')

        if 'next' in data:
            next = data.next
        else:
            break

    print('Done.')


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    update_firmware(api)
