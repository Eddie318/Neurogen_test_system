#!/usr/bin/env python3
"""
初始化团队题库系统数据库
"""

import sqlite3
from datetime import datetime

def init_team_system():
    """初始化团队题库系统"""
    db_path = "/Users/jiaxuanmu/Desktop/code/Neurogen_test_system/python-backend/exam_system.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🚀 开始初始化团队题库系统...")
        
        # 1. 创建产品团队表
        print("📋 创建产品团队表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                wechat_dept_id VARCHAR(100),
                wechat_mapping JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 创建题库表
        print("📚 创建题库表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_banks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES product_teams(id)
            )
        """)
        
        # 3. 检查questions表是否存在bank_id字段
        print("🔧 检查题目表结构...")
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'bank_id' not in columns:
            print("➕ 添加bank_id字段到题目表...")
            cursor.execute("ALTER TABLE questions ADD COLUMN bank_id INTEGER DEFAULT 1")
        
        # 4. 检查exam_records表是否存在team_id和bank_id字段
        print("🔧 检查考试记录表结构...")
        cursor.execute("PRAGMA table_info(exam_records)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'team_id' not in columns:
            print("➕ 添加team_id字段到考试记录表...")
            cursor.execute("ALTER TABLE exam_records ADD COLUMN team_id INTEGER DEFAULT 1")
            
        if 'bank_id' not in columns:
            print("➕ 添加bank_id字段到考试记录表...")
            cursor.execute("ALTER TABLE exam_records ADD COLUMN bank_id INTEGER DEFAULT 1")
        
        # 5. 插入默认团队
        print("🏢 插入默认团队数据...")
        cursor.execute("""
            INSERT OR IGNORE INTO product_teams (id, name, code, description) 
            VALUES (1, '默认团队', 'default', '系统默认团队，包含所有现有题目')
        """)
        
        # 6. 插入默认题库
        print("📖 插入默认题库数据...")
        cursor.execute("""
            INSERT OR IGNORE INTO question_banks (id, team_id, name, description)
            VALUES (1, 1, '默认题库', '系统默认题库，包含所有现有题目')
        """)
        
        # 7. 更新所有现有题目的bank_id为1
        print("🔄 更新现有题目关联到默认题库...")
        cursor.execute("UPDATE questions SET bank_id = 1 WHERE bank_id IS NULL OR bank_id = 0")
        
        # 8. 更新所有现有考试记录的team_id和bank_id为1
        print("🔄 更新现有考试记录关联到默认团队题库...")
        cursor.execute("UPDATE exam_records SET team_id = 1 WHERE team_id IS NULL OR team_id = 0")
        cursor.execute("UPDATE exam_records SET bank_id = 1 WHERE bank_id IS NULL OR bank_id = 0")
        
        # 9. 添加系统配置项
        print("⚙️ 添加系统配置项...")
        current_time = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO system_config (key, value, description, config_type, updated_at)
            VALUES ('current_team_id', '1', '当前活动的团队ID', 'number', ?)
        """, (current_time,))
        
        cursor.execute("""
            INSERT OR REPLACE INTO system_config (key, value, description, config_type, updated_at)
            VALUES ('current_bank_id', '1', '当前活动的题库ID', 'number', ?)
        """, (current_time,))
        
        # 提交事务
        conn.commit()
        
        # 10. 验证数据
        print("✅ 验证初始化结果...")
        
        # 检查团队数据
        cursor.execute("SELECT COUNT(*) FROM product_teams")
        team_count = cursor.fetchone()[0]
        print(f"   - 团队数量: {team_count}")
        
        # 检查题库数据
        cursor.execute("SELECT COUNT(*) FROM question_banks")
        bank_count = cursor.fetchone()[0]
        print(f"   - 题库数量: {bank_count}")
        
        # 检查题目关联
        cursor.execute("SELECT COUNT(*) FROM questions WHERE bank_id = 1")
        question_count = cursor.fetchone()[0]
        print(f"   - 默认题库题目数量: {question_count}")
        
        # 检查考试记录关联
        cursor.execute("SELECT COUNT(*) FROM exam_records WHERE team_id = 1 AND bank_id = 1")
        record_count = cursor.fetchone()[0]
        print(f"   - 默认团队考试记录数量: {record_count}")
        
        print("🎉 团队题库系统初始化完成！")
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = init_team_system()
    if success:
        print("\n✨ 可以启动服务器测试新功能了！")
    else:
        print("\n💥 初始化失败，请检查错误信息")