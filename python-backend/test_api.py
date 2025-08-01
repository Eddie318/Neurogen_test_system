#!/usr/bin/env python3
"""
FastAPI服务器测试脚本
"""

import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8002"
    
    print("🚀 测试FastAPI服务器")
    print("=" * 50)
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查: 正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")
        return
    
    print()
    
    # 测试各个API端点
    apis = [
        ("考试记录", "/api/exam-records"),
        ("主配置", "/api/master-config"),
        ("题库", "/api/master-questions"),
        ("API文档", "/docs"),
    ]
    
    for name, endpoint in apis:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                if endpoint == "/docs":
                    print(f"✅ {name}: 可访问")
                else:
                    data = response.json()
                    if endpoint == "/api/exam-records":
                        count = len(data) if isinstance(data, list) else 0
                        print(f"✅ {name}: {count}条记录")
                    elif endpoint == "/api/master-questions":
                        total = data.get('totalQuestions', 0)
                        print(f"✅ {name}: {total}道题目")
                    else:
                        print(f"✅ {name}: 正常")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print()
    print("📋 访问地址:")
    print(f"- API文档: {base_url}/docs")
    print(f"- 健康检查: {base_url}/health")
    print(f"- 题库: {base_url}/api/master-questions")
    print(f"- 考试记录: {base_url}/api/exam-records")
    print(f"- 配置: {base_url}/api/master-config")

if __name__ == "__main__":
    test_api()