#!/usr/bin/env python3
"""
使用curl命令测试API导入数据
"""

import json
import os
import requests

def import_questions():
    """导入题库数据"""
    print("🔄 导入题库数据...")
    
    # 寻找题库文件
    json_file_paths = [
        "../local-deploy/data/master-questions.json",
        "../local-clean-version/data/master-questions.json", 
        "../docker-deploy/data/master-questions.json",
        "./master-questions.json"
    ]
    
    json_file = None
    for path in json_file_paths:
        if os.path.exists(path):
            json_file = path
            print(f"✅ 找到题库文件: {path}")
            break
    
    if not json_file:
        print("❌ 找不到题库JSON文件")
        print("请检查以下路径：")
        for path in json_file_paths:
            print(f"  - {path}")
        return False
    
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = data.get('questions', [])
        print(f"📖 读取到 {len(questions)} 道题目")
        
        # 发送到API服务器
        print("🚀 发送数据到API服务器...")
        response = requests.post(
            'http://localhost:8001/api/questions/import', 
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', '导入成功')}")
            return True
        else:
            print(f"❌ 导入失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("请确保已启动服务器: python start.py")
        return False
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_apis():
    """测试API端点"""
    print("\n🧪 测试API端点...")
    
    apis = [
        ("健康检查", "http://localhost:8001/health"),
        ("获取题库", "http://localhost:8001/api/master-questions"),
        ("获取配置", "http://localhost:8001/api/master-config"),
        ("获取考试记录", "http://localhost:8001/api/exam-records")
    ]
    
    for name, url in apis:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if name == "获取题库":
                    total = data.get('totalQuestions', 0)
                    print(f"✅ {name}: 成功 (共{total}道题目)")
                elif name == "获取考试记录":
                    count = len(data) if isinstance(data, list) else 0
                    print(f"✅ {name}: 成功 (共{count}条记录)")
                else:
                    print(f"✅ {name}: 成功")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 错误 - {e}")

def main():
    print("🚀 穆桥销售测验系统 - API测试工具")
    print("=" * 50)
    
    # 导入数据
    success = import_questions()
    
    if success:
        # 测试API
        test_apis()
        
        print("\n" + "=" * 50)
        print("🎉 测试完成！")
        print("\n📋 下一步:")
        print("1. 访问 http://localhost:8001/docs 查看API文档")
        print("2. 在Swagger UI中测试各个接口")
        print("3. 修改前端页面调用这些API")
        
        print("\n🔗 API地址:")
        print("- 题库: http://localhost:8001/api/master-questions")
        print("- 配置: http://localhost:8001/api/master-config") 
        print("- 记录: http://localhost:8001/api/exam-records")
    else:
        print("\n❌ 数据导入失败，请检查错误信息")

if __name__ == "__main__":
    main()