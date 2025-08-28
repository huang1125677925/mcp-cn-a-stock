#!/bin/bash

# SSE接口启动脚本

# 激活虚拟环境
source venv/bin/activate

# 设置默认端口
PORT=${1:-8080}

# 启动SSE服务
echo "启动A股数据MCP服务 (SSE模式)..."
echo "端口: $PORT"
echo "访问地址: http://localhost:$PORT"
echo "SSE端点: http://localhost:$PORT/sse"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python3 main.py --transport sse --port $PORT