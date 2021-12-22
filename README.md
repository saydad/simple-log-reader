# simple-log-reader
## 功能
1. 用于读取服务器日志，可以自动切换文件
2. 可以通过修改handle_content方法扩展对文件内容的处理，例如：发送给远端提醒

## 注意事项
1. 启动脚本时，读取的文件需要存在
2. 读取进度(已读取的字节)默认存储在/tmp/log-read-record文件

## 使用方式
1. 编辑 log-reader.py脚本中config_json变量，修改为需要关注的日志文件目录与文件前缀名称
```json
[
  {
    "path": "/tmp",
    "filePrefixName": "test"
  }
]
```
2. 执行 log-reader.py脚本，每个配置项会分配一个线程进行读取，main线程负责定时将读取进度写入本地文件(/tmp/log-read-record)
