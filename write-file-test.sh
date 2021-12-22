#!/bin/bash
# 在/tmp目录下获取test.log.*下标最大的文件，如果不存在则创建test.log.0
target_file=$(ls /tmp | grep test | sort -nr | head -n1)
if [ ${#target_file} -le 0 ]; then
  touch "/tmp/test.log.0"
  index=0
  target_file="/tmp/test.log.0"
else
  index=$(echo "$target_file" | awk -F . '{print $3}')
  target_file="/tmp/"$target_file
fi 
echo "$target_file"

# 写入数据，30秒切换一个新文件
start_time_second=$(date +%s)
while [ 1 ]; do
    sleep 0.5
    cur_time_second=$(date +%s)
    diff=$[$cur_time_second - $start_time_second]
    if [ "$diff" -ge "30" ]; then
      index=$[$index + 1]
      echo "touch /tmp/test.log.""$index"
      start_time_second=$cur_time_second
      touch "/tmp/test.log.""$index"
      target_file="/tmp/test.log.""$index"
    fi
    echo "$cur_time_second" >> "$target_file"
done
