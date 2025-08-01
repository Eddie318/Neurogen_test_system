#!/usr/bin/env python3
"""
穆桥销售测验系统 - Python后端启动脚本
"""

import uvicorn
import os
import sys

def main():
    print("🐍 穆桥销售测验系统 - Python后端")
    print("=" * 50)
    print("🚀 启动FastAPI服务器...")
    print("📡 监听地址: http://0.0.0.0:8002")
    print("📚 API文档: http://localhost:8002/docs")
    print("🔧 管理界面: http://localhost:8002/redoc")
    print("=" * 50)
    print("⌨️  按 Ctrl+C 停止服务器")
    print()
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,  # 开发模式，文件变化时自动重启
        access_log=True
    )

if __name__ == "__main__":
    main()