#!/bin/bash
echo "停止穆桥销售测验系统..."
pkill -f "node.*sync-server" 2>/dev/null
pkill -f "python.*8000" 2>/dev/null
echo "服务已停止"
