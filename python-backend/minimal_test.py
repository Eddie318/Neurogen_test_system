#!/usr/bin/env python3
"""
最小化测试服务器 - 确保基本网络功能正常
"""

import http.server
import socketserver
import json

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"收到GET请求: {self.path}")
        
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "message": "测试服务器正常运行"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = "<h1>测试服务器运行正常</h1><p>访问 /health 查看健康状态</p>"
            self.wfile.write(html.encode('utf-8'))

def main():
    PORT = 8003
    print(f"🧪 启动最小化测试服务器")
    print(f"📡 监听端口: {PORT}")
    print(f"🌐 访问地址: http://localhost:{PORT}")
    print(f"💚 健康检查: http://localhost:{PORT}/health")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
            print(f"服务器启动成功，监听端口 {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()