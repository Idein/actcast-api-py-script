# -*- coding: utf-8 -*-
from os import path
import sys
import time
import csv
from actcast_api import ActcastAPI, Color

page_limit = 100
request_interval_msec = 1000


def ls_device_status(api, out_path, page_id=''):
    next = ''
    page_start = 0

    # PageIDの指定があれば途中のページから始められるようにする
    if page_id != '':
        next = page_id
        page_start = (api.next2json(next)['offset'] // page_limit)

    ##################################################
    # デバイス総数と必要ページネーション回数を求める
    ##################################################
    params = {}
    params.update({'limit': page_limit})
    params.update({'include_status': 1})
    if isinstance(next, int):
        params.update({'next': next})

    data = api.get_devices_list(query_params=params)

    device_total = data.total
    page_end = (-1 * (-device_total // page_limit))  # 切り上げ

    print(f'device_total: {device_total}    page_limit:{page_limit}')
    print(f'execute: {page_start}-{page_end} page')
    print('=' * 80)

    with open(out_path, 'w', newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['index', 'device_id', 'hardware_id', 'mac_addr', 'hostname',
                         'host_version', 'device_type', 'foundness', 'firmware_version', 'firmware_version_timestamp',
                         'access_points', 'connected_ssid', 'country_code', 'tags', 'disk',
                         'disk_usage', 'memory', 'memory_usage', 'cpu_temperature', 'act_latest_event',
                         'act_id', 'act_name', 'act_artifact_id', 'reported_act_id', 'reported_act_name',
                         'reported_act_artifact_id', 'reported_act_installed_at', 'act_status'
                         ])

        ##################################################
        # ページネーション
        ##################################################
        for page in range(page_start, page_end):
            time.sleep(request_interval_msec / 1000)

            print(f'\nPageID => {next}')

            params.update({'limit': page_limit})
            params.update({'include_status': 1})
            if isinstance(next, int):
                params.update({'next': next})
            data = api.get_devices_list(query_params=params)

            if data is False:
                print(Color.RED + 'ERROR: Could not get device list.' +
                      Color.COLOR_DEFAULT)
                sys.exit(1)

            # 1ページ分処理
            for i, item in enumerate(data.items, 1):
                index = (page * page_limit) + i

                # act情報の取得
                if item.device.act is None:
                    act_id = act_name = act_artifact_id = 'None'
                else:
                    act_id = item.device.act.id if hasattr(
                        item.device.act, 'id') else 'None'
                    act_name = item.device.act.name if hasattr(
                        item.device.act, 'name') else 'None'
                    act_artifact_id = item.device.act.artifact_id if hasattr(
                        item.device.act, 'artifact_id') else 'None'

                device_id = item.device.id
                hardware_id = item.device.hardware_id if hasattr(
                    item.device, 'hardware_id') else 'None'
                mac_addr = item.device.mac_addr if hasattr(
                    item.device, 'mac_addr') else 'None'
                hostname = item.device.hostname if hasattr(
                    item.device, 'hostname') else 'None'
                host_version = item.device.host_version if hasattr(
                    item.device, 'host_version') else 'None'
                device_type = item.device.device_type if hasattr(
                    item.device, 'device_type') else 'None'
                foundness = item.device.foundness if hasattr(
                    item.device, 'foundness') else 'None'
                firmware_version = item.device.firmware_version if hasattr(
                    item.device, 'firmware_version') else 'None'
                firmware_version_timestamp = item.device.firmware_version_timestamp if hasattr(
                    item.device, 'firmware_version_timestamp') else 'None'
                access_points = item.device.access_points if hasattr(
                    item.device, 'access_points') else 'None'
                tags = item.device.tags if hasattr(
                    item.device, 'tags') else 'None'
                country_code = item.device.country_code if hasattr(
                    item.device, 'country_code') else 'None'

                # なぜかNULL文字が含まれている場合の対処
                hardware_id = hardware_id.replace('\0', '')

                # statusがない時
                if not hasattr(item, 'status'):
                    connected_ssid = disk = disk_usage = memory = memory_usage = cpu_temperature = act_latest_event = act_status = 'None'
                # statusがある時
                else:
                    connected_ssid = item.status.connected_ssid if hasattr(
                        item.status, 'id') else 'None'
                    disk = item.status.disk if hasattr(
                        item.status, 'disk') else 'None'
                    disk_usage = item.status.disk_usage if hasattr(
                        item.status, 'disk_usage') else 'None'
                    memory = item.status.memory if hasattr(
                        item.status, 'memory') else 'None'
                    memory_usage = item.status.memory_usage if hasattr(
                        item.status, 'memory_usage') else 'None'
                    cpu_temperature = item.status.cpu_temperature if hasattr(
                        item.status, 'cpu_temperatur') else 'None'
                    act_latest_event = item.status.act_latest_event if hasattr(
                        item.status, 'act_latest_event') else 'None'
                    act_status = item.status.act_status if hasattr(
                        item.status, 'act_status') else 'None'

                # reported_actがない時
                if not hasattr(item.device, 'reported_act'):
                    reported_act_id = reported_act_name = reported_act_artifact_id = reported_act_installed_at = 'None'
                # reported_actがある時
                else:
                    reported_act_id = item.device.reported_act.id if hasattr(
                        item.device.reported_act, 'id') else 'None'
                    reported_act_name = item.device.reported_act.name if hasattr(
                        item.device.reported_act, 'name') else 'None'
                    reported_act_artifact_id = item.device.reported_act.artifact_id if hasattr(
                        item.device.reported_act, 'artifact_id') else 'None'
                    reported_act_installed_at = item.device.reported_act.installed_at if hasattr(
                        item.device.reported_act, 'installed_at') else 'None'

                print(f'{device_id} {index:6d}/{device_total}')
                # print(f'{device_id},{hardware_id},{mac_addr},{hostname},{host_version},{device_type},{foundness},{firmware_version},{firmware_version_timestamp},{access_points},{connected_ssid},{country_code},{tags,disk,disk_usage},{memory,memory_usage},{cpu_temperature},{act_latest_event},{act_id,act_name},{act_artifact_id},{reported_act_id},{reported_act_name},{reported_act_artifact_id},{reported_act_installed_at},{act_status} {index:6d}/{device_total}')

                # CSVに吐き出し
                writer.writerow([index, device_id, hardware_id, mac_addr, hostname, host_version, device_type, foundness, firmware_version, firmware_version_timestamp, access_points, connected_ssid, country_code, tags, disk,
                                disk_usage, memory, memory_usage, cpu_temperature, act_latest_event, act_id, act_name, act_artifact_id, reported_act_id, reported_act_name, reported_act_artifact_id, reported_act_installed_at, act_status])

            if 'next' in data:
                next = data.next

    print('=' * 80)
    print('Done.')


if __name__ == '__main__':
    api = ActcastAPI()

    args = sys.argv
    if len(args) < 2:
        print("usage:")
        print(
            f"$ python3 {path.basename(__file__)} output_path [page_id]")
    elif len(args) == 2:
        output_path = args[1]
        ls_device_status(api, output_path)
    else:
        output_path = args[1]
        page_id = args[2]
        ls_device_status(api, output_path, page_id)
