#!/bin/bash

# 获取进程信息
ps_output=$(ps -eo pid,comm,state,cmd)

# 打印表头
echo "PID COMMAND STATE CMD PORT"

# 逐行处理 ps 输出
while IFS= read -r line; do
    # 提取 PID
    pid=$(echo "$line" | awk '{print \$1}')

    # 获取端口号
    port=$(ss -tulnpe 2>/dev/null | grep "pid=$pid" | awk -F'[:,]' '{print \$8}')

    # 打印结果
    echo "$line $port"
done <<< "$ps_output"
