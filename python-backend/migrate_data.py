#!/usr/bin/env python3
"""
数据迁移脚本
从现有的JSON文件导入数据到数据库
"""

import json
import os
import sys
from datetime import datetime

# 添加app目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, engine
from app.models import Base, Question, SystemConfig

def migrate_questions():
    """迁移题库数据"""
    print("🔄 开始迁移题库数据...")
    
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
        
        questions = data.get('questions', [])
        print(f"📖 读取到 {len(questions)} 道题目")
        
        db = SessionLocal()
        
        # 清空现有题库（可选）
        # db.query(Question).delete()
        
        imported_count = 0
        for q_data in questions:
            # 检查是否已存在
            existing = db.query(Question).filter(
                Question.question == q_data["question"]
            ).first()
            
            if existing:
                print(f"⚠️  题目已存在，跳过: {q_data['question'][:50]}...")
                continue
            
            # 创建新题目
            db_question = Question(
                category=q_data["category"],
                question_type=q_data["type"],
                question=q_data["question"],
                option_a=q_data["optionA"],
                option_b=q_data["optionB"],
                option_c=q_data.get("optionC"),
                option_d=q_data.get("optionD"),
                answer=q_data["answer"],
                explanation=q_data.get("explanation", ""),
                question_id=q_data.get("questionId")
            )
            
            db.add(db_question)
            imported_count += 1
        
        db.commit()
        print(f"✅ 成功导入 {imported_count} 道题目")
        
        # 统计结果
        total_questions = db.query(Question).count()
        print(f"📊 数据库中共有 {total_questions} 道题目")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

def migrate_config():
    """迁移配置数据"""
    print("🔄 开始迁移配置数据...")
    
    # 寻找配置文件
    config_file_paths = [
        "../local-deploy/data/master-config.json",
        "../local-clean-version/data/master-config.json",
        "./master-config.json"
    ]
    
    config_file = None
    for path in config_file_paths:
        if os.path.exists(path):
            config_file = path
            break
    
    if not config_file:
        print("❌ 找不到配置JSON文件")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        db = SessionLocal()
        
        # 导入API配置
        if 'apiConfig' in data:
            api_config = SystemConfig(
                key="api_config",
                value=json.dumps(data['apiConfig']),
                description="通义千问API配置",
                config_type="json"
            )
            
            # 检查是否已存在
            existing = db.query(SystemConfig).filter(
                SystemConfig.key == "api_config"
            ).first()
            
            if existing:
                existing.value = json.dumps(data['apiConfig'])
                existing.updated_at = datetime.now()
                print("✅ 更新API配置")
            else:
                db.add(api_config)
                print("✅ 导入API配置")
        
        # 导入系统信息
        if 'systemInfo' in data:
            system_info = SystemConfig(
                key="system_info",
                value=json.dumps(data['systemInfo']),
                description="系统基础信息",
                config_type="json"
            )
            
            existing = db.query(SystemConfig).filter(
                SystemConfig.key == "system_info"
            ).first()
            
            if existing:
                existing.value = json.dumps(data['systemInfo'])
                existing.updated_at = datetime.now()
                print("✅ 更新系统信息")
            else:
                db.add(system_info)
                print("✅ 导入系统信息")
        
        db.commit()
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 配置迁移失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 穆桥销售测验系统 - 数据迁移工具")
    print("=" * 50)
    
    # 创建数据库表
    print("📦 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    # 迁移题库
    questions_success = migrate_questions()
    
    # 迁移配置
    config_success = migrate_config()
    
    print("\n" + "=" * 50)
    if questions_success and config_success:
        print("🎉 数据迁移完成！")
        print("\n📋 下一步:")
        print("1. 运行 python start.py 启动服务器")
        print("2. 访问 http://localhost:8001 查看API文档")
        print("3. 测试API接口功能")
    else:
        print("⚠️  数据迁移部分完成，请检查错误信息")

if __name__ == "__main__":
    main()