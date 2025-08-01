#!/usr/bin/env python3
"""
简化启动脚本 - 避免复杂依赖问题
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_path = "exam_system.db"
        self.init_db()
        super().__init__(*args, **kwargs)
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建题库表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question_type TEXT NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT,
                option_d TEXT,
                answer TEXT NOT NULL,
                explanation TEXT,
                question_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建考试记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_records (
                id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                detailed_answers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)
        
        if path == '/':
            self.send_homepage()
        elif path == '/api/master-questions':
            self.send_questions(params.get('sales', [False])[0])
        elif path == '/api/exam-records':
            self.send_exam_records()
        elif path == '/api/master-config':
            self.send_config()
        elif path == '/health':
            self.send_json({'status': 'healthy'})
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/exam-records':
            self.save_exam_record()
        elif path == '/api/questions/import':
            self.import_questions()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """发送CORS头部"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def send_json(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def send_homepage(self):
        """发送主页"""
        html = '''
        <html>
        <head>
            <title>穆桥销售测验系统 - 简化Python后端</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🐍 穆桥销售测验系统 - 简化Python后端</h1>
            <p>系统运行正常！</p>
            
            <h2>📋 可用API接口：</h2>
            <ul>
                <li><a href="/api/master-questions">🗂️ 获取题库</a></li>
                <li><a href="/api/exam-records">📊 考试记录</a></li>
                <li><a href="/api/master-config">⚙️ 系统配置</a></li>
                <li><a href="/health">💚 健康检查</a></li>
            </ul>
            
            <h2>🔧 使用说明：</h2>
            <ol>
                <li>运行 <code>python import_data.py</code> 导入现有数据</li>
                <li>将前端页面的localStorage调用改为API调用</li>
                <li>测试移动端和PC端访问</li>
            </ol>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_questions(self, is_sales=False):
        """发送题库数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM questions')
        rows = cursor.fetchall()
        
        questions = []
        categories = set()
        
        for row in rows:
            question_data = {
                "id": row[0],
                "category": row[1],
                "type": row[2],
                "question": row[3],
                "optionA": row[4],
                "optionB": row[5],
                "optionC": row[6],
                "optionD": row[7],
                "questionId": row[10] or row[0]
            }
            
            # 销售模式下不返回答案
            if not is_sales:
                question_data["answer"] = row[8]
                question_data["explanation"] = row[9] or ""
            
            questions.append(question_data)
            categories.add(row[1])
        
        conn.close()
        
        result = {
            "version": 2,
            "lastUpdate": datetime.now().isoformat(),
            "totalQuestions": len(questions),
            "categories": list(categories),
            "maintainer": "管理员",
            "questions": questions
        }
        
        self.send_json(result)
    
    def send_exam_records(self):
        """发送考试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM exam_records ORDER BY created_at DESC LIMIT 100')
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            record = {
                "id": row[0],
                "userName": row[1],
                "score": row[2],
                "correctCount": row[3],
                "totalQuestions": row[4],
                "duration": row[5],
                "timestamp": row[7]
            }
            if row[6]:  # detailed_answers
                try:
                    record["questions"] = json.loads(row[6])
                except:
                    pass
            records.append(record)
        
        conn.close()
        self.send_json(records)
    
    def send_config(self):
        """发送配置信息"""
        config = {
            "version": 1,
            "lastUpdate": datetime.now().isoformat(),
            "apiConfig": {
                "provider": "qwen",
                "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                "model": "qwen-turbo",
                "key": os.getenv("QWEN_API_KEY", "sk-4b10986087d4481e88acdc0378c56e6f"),
                "enabled": True
            },
            "systemInfo": {
                "title": "穆桥销售测验系统",
                "description": "专业销售知识测评平台",
                "examDuration": 30,
                "questionsPerExam": 15,
                "passingScore": 60
            },
            "permissions": {
                "allowAdminEdit": True,
                "allowApiEdit": True,
                "allowQuestionEdit": True
            }
        }
        self.send_json(config)
    
    def save_exam_record(self):
        """保存考试记录"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO exam_records 
                (id, user_name, score, correct_count, total_questions, duration, detailed_answers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('id'),
                data.get('userName'),
                data.get('score'),
                data.get('correctCount'),
                data.get('totalQuestions'),
                data.get('duration'),
                json.dumps(data.get('questions', []))
            ))
            
            conn.commit()
            conn.close()
            
            self.send_json({
                "success": True,
                "message": "考试记录保存成功"
            })
            
        except Exception as e:
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode('utf-8'))
    
    def import_questions(self):
        """导入题库数据"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            questions = data.get('questions', [])
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            for q in questions:
                # 检查是否已存在
                cursor.execute('SELECT id FROM questions WHERE question = ?', (q['question'],))
                if cursor.fetchone():
                    continue
                
                cursor.execute('''
                    INSERT INTO questions 
                    (category, question_type, question, option_a, option_b, option_c, option_d, answer, explanation, question_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q.get('category'),
                    q.get('type'),
                    q.get('question'),
                    q.get('optionA'),
                    q.get('optionB'),
                    q.get('optionC'),
                    q.get('optionD'),
                    q.get('answer'),
                    q.get('explanation', ''),
                    q.get('questionId')
                ))
                imported_count += 1
            
            conn.commit()
            conn.close()
            
            self.send_json({
                "success": True,
                "message": f"成功导入 {imported_count} 道题目"
            })
            
        except Exception as e:
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode('utf-8'))

def main():
    print("🐍 穆桥销售测验系统 - 简化Python后端")
    print("=" * 50)
    print("🚀 启动HTTP服务器...")
    print("📡 监听地址: http://0.0.0.0:8001")
    print("🌐 访问地址: http://localhost:8001")
    print("=" * 50)
    print("⌨️  按 Ctrl+C 停止服务器")
    print()
    
    try:
        server = HTTPServer(('0.0.0.0', 8001), SimpleAPIHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

if __name__ == "__main__":
    main()