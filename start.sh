#!/bin/bash

# 先杀掉之前的python3 main.py进程
pkill -f "python3 main.py"

# 等待进程完全结束
sleep 2

# 启动新的进程
nohup python3 main.py > log.txt 2>&1 &

echo "已重启 main.py 进程"
echo "进程PID: $!"
echo "日志文件: log.txt"