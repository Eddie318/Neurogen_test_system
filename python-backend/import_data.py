#!/usr/bin/env python3
"""
简化数据导入脚本
"""

import json
import os
import requests
import sys

def import_questions():
    """导入题库数据"""
    print("🔄 导入题库数据...")
    
    # 寻找题库文件
    json_file_paths = [
        "../local-deploy/data/master-questions.json",
        "../local-clean-version/data/master-questions.json",
        "./master-questions.json"
    ]
    
    json_file = None
    for path in json_file_paths:
        if os.path.exists(path):
            json_file = path
            break
    
    if not json_file:
        print("❌ 找不到题库JSON文件")
        return False
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📖 读取到 {len(data.get('questions', []))} 道题目")
        
        # 发送到API服务器
        response = requests.post('http://localhost:8001/api/questions/import', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', '导入成功')}")
            return True
        else:
            print(f"❌ 导入失败: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请先启动 python simple_start.py")
        return False
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def main():
    print("🚀 穆桥销售测验系统 - 数据导入工具")
    print("=" * 50)
    
    success = import_questions()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 数据导入完成！")
        print("\n📋 下一步:")
        print("1. 访问 http://localhost:8001 查看API")
        print("2. 测试API接口")
        print("3. 修改前端页面调用API")
    else:
        print("⚠️  数据导入失败，请检查错误信息")

if __name__ == "__main__":
    main()