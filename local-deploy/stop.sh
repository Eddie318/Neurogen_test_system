#!/bin/bash
echo "停止穆桥销售测验系统..."
pkill -f "python.*8000" 2>/dev/null
echo "Web服务器已停止"
