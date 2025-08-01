#!/usr/bin/env python3
"""
调试服务器 - 最简单的版本
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

class DebugHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Server is running!</h1><p>Debug mode active</p>')
        
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        
        elif self.path == '/api/master-questions':
            # 直接读取JSON文件并返回
            json_paths = [
                "../local-deploy/data/master-questions.json",
                "../docker-deploy/data/master-questions.json"
            ]
            
            for path in json_paths:
                if os.path.exists(path):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                        return
                    except Exception as e:
                        break
            
            # 如果没找到文件
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "题库文件未找到"}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def main():
    print("🔧 调试服务器启动")
    print("访问: http://localhost:8002")
    print("题库: http://localhost:8002/api/master-questions")
    print("健康: http://localhost:8002/health")
    
    server = HTTPServer(('localhost', 8002), DebugHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")

if __name__ == "__main__":
    main()