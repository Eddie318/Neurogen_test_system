from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
from .database import engine, get_db
from .models import Base
from .routers import questions, exams, admin, exam_management
from .config import settings

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="穆桥销售测验系统 - Python后端",
    description="医药代表考试系统API",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地开发允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(questions.router, prefix="/api", tags=["题库管理"])
app.include_router(exams.router, prefix="/api", tags=["考试系统"])
app.include_router(admin.router, prefix="/api", tags=["后台管理"])
app.include_router(exam_management.router, prefix="/api", tags=["考试管理"])

# 静态文件服务
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页"""
    return """
    <html>
        <head>
            <title>穆桥销售测验系统 - Python后端</title>
            <meta charset="utf-8">
        </head>
        <body>
            <div style="max-width: 800px; margin: 50px auto; padding: 20px; font-family: Arial, sans-serif;">
                <h1>🐍 穆桥销售测验系统 - Python后端</h1>
                <p>系统已启动成功！</p>
                
                <h2>📋 可用功能：</h2>
                <ul>
                    <li><a href="/static/vue-exam-new.html" target="_blank">🎯 新版考试系统（支持正式考试+随机练习）</a></li>
                    <li><a href="/static/vue-exam.html" target="_blank">🔧 旧版随机考试系统</a></li>
                    <li><a href="/static/vue-admin.html" target="_blank">📊 Vue管理后台（含考试创建）</a></li>
                    <li><a href="/docs" target="_blank">📚 API文档 (Swagger)</a></li>
                    <li><a href="/redoc" target="_blank">📖 API文档 (ReDoc)</a></li>
                    <li><a href="/api/questions" target="_blank">🗂️ 获取题库</a></li>
                    <li><a href="/api/exam-records" target="_blank">📊 考试记录</a></li>
                </ul>
                
                <h2>🔧 测试步骤：</h2>
                <ol>
                    <li>点击上面的API文档链接</li>
                    <li>测试各个API端点</li>
                    <li>确认数据正常返回</li>
                    <li>集成前端页面</li>
                </ol>
                
                <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <strong>💡 下一步：</strong> 将现有前端页面修改为调用这些API接口
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "穆桥销售测验系统运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)