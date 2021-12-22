# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import os
import threading
from time import sleep

# 配置项,需要读取的文件所在的目录与文件名称前缀
config_json = '[{"path":"/tmp","filePrefixName":"test"}]'
# 读取进度内存存储，用于落在/tmp/log-read-record,从而下次启动后可以继续读取
record_map = {}


# 解析配置，并建立文件读取任务
def parse_config():
    config_list = json.loads(config_json)
    if not config_list:
        return
    load_read_record(config_list)

    thread_list = []
    path_file_list_map = {}
    for config in config_list:
        sorted_file_list = path_file_list_map.get(config['path'])
        if not sorted_file_list:
            sorted_file_list = file_create_time_desc_list(config['path'])
            path_file_list_map[config['path']] = sorted_file_list
        target_file = file_choose(config['path'], config['filePrefixName'], sorted_file_list)
        record = record_map.get(config['path'] + os.sep + config['filePrefixName'])
        # 为每一个文件创建一个线程
        thread_list.append(LogReadThread(record, config['path'], config['filePrefixName'], target_file))
    return thread_list


# 加载本地记录到内存中，同时对新增的配置也加载到内存
def load_read_record(config_list):
    lines = []
    exist_flag = os.path.exists("/tmp/log-read-record")
    if exist_flag:
        with open("/tmp/log-read-record", "r") as file:
            lines = file.readlines()

    for line in lines:
        content = line.split(" ")
        record_map[content[0]] = int(content[1])

    for config in config_list:
        full_key = config['path'] + os.sep + config['filePrefixName']
        record = record_map.get(full_key)
        if not record:
            record_map[full_key] = 0


# 将record_map写入到文件中
def store_record_map():
    if len(record_map) <= 0:
        return

    lines = []
    item_list = record_map.items()
    for key, value in item_list:
        lines.append(key + " " + str(value) + os.linesep)

    with open("/tmp/log-read-record", "w") as file:
        file.writelines(lines)


# 文件选择，如果当前文件大小小于文件读取记录则取下一个文件
def file_choose(path, file_prefix_name, sorted_file_list):
    full_path = path + os.sep + file_prefix_name
    record = record_map.get(full_path)
    target_file = ""
    first_file_skip = False
    for absolute_file_name in sorted_file_list:
        if absolute_file_name.startswith(full_path):
            if not first_file_skip:
                first_file_skip = True
            else:
                target_file = absolute_file_name
                break
            if file_count(absolute_file_name) >= record:
                target_file = absolute_file_name
                break
    return target_file


# 获取指定目录下所有文件,文件按照创建时间倒序
def file_create_time_desc_list(target_file_path):
    file_name_list = []
    all_content = os.walk(target_file_path)
    for file_path, dir_list, file_list in all_content:
        for file_name in file_list:
            file_name_list.append(os.path.join(file_path, file_name))
    file_name_list = sorted(file_name_list, key=lambda x: os.path.getctime(x), reverse=True)
    return file_name_list


# 获取文件行数
def file_count(file_name):
    if not os.path.exists(file_name):
        return 0

    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_name) as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count(os.linesep) for buf in buf_gen)


class LogReadThread(threading.Thread):
    record = 0
    path = ""
    file_prefix_name = ""
    full_key = ""
    target_file_name = ""

    def __init__(self, record, path, file_prefix_name, target_file_name):
        threading.Thread.__init__(self)
        self.record = record
        self.path = path
        self.file_prefix_name = file_prefix_name
        self.full_key = self.path + os.sep + self.file_prefix_name
        self.target_file_name = target_file_name

    def run(self) -> None:
        while True:
            print('read ' + self.target_file_name)
            with open(self.target_file_name, 'r') as f:
                f.seek(self.record)
                while True:
                    line = f.readline()
                    if len(line) > 0:
                        handle_content(line)
                        # 更新记录值
                        self.record = f.tell()
                        record_map[self.full_key] = self.record
                    else:
                        sorted_file_list = file_create_time_desc_list(self.path)
                        sorted_file_list = [item for item in sorted_file_list if item.startswith(self.full_key)]
                        index = sorted_file_list.index(self.target_file_name)
                        if index > 0:
                            self.target_file_name = sorted_file_list[0]
                            self.record = 0
                            break


# 如果处理从文件中读取的内容，默认为打印到控制台，可以远程发送，从而实现一个简单的日志监控
def handle_content(line):
    print(line)


# 实现tail -f file.* 的功能，但是可以自动切换文件
if __name__ == '__main__':
    task_list = parse_config()
    for task in task_list:
        task.daemon = True
        task.start()

    # 定时存储读取进度记录
    while True:
        sleep(1)
        store_record_map()
