# 穆桥销售测验系统 - Python后端

基于FastAPI的医药代表考试系统后端服务，支持题库管理、考试记录、AI报告生成等功能。

## 🚀 快速开始

### 1. 安装依赖
```bash
cd python-backend
pip install -r requirements.txt
```

### 2. 环境配置
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件，设置API密钥
nano .env
```

### 3. 数据迁移
```bash
# 从现有JSON文件导入数据
python migrate_data.py
```

### 4. 启动服务
```bash
# 开发模式启动
python start.py

# 或直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 5. 访问服务
- **API文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc  
- **健康检查**: http://localhost:8001/health

## 📋 主要功能

### API端点

#### 题库管理
- `GET /api/questions` - 获取题库列表
- `GET /api/master-questions` - 获取完整题库（兼容现有格式）
- `POST /api/questions` - 创建题目
- `PUT /api/questions/{id}` - 更新题目
- `DELETE /api/questions/{id}` - 删除题目
- `POST /api/questions/import` - 批量导入题目

#### 考试系统
- `GET /api/exam-records` - 获取考试记录
- `POST /api/exam-records` - 保存考试记录
- `GET /api/exam-records/{id}` - 获取单个记录详情
- `DELETE /api/exam-records/{id}` - 删除考试记录
- `POST /api/generate-ai-report` - 生成AI分析报告
- `GET /api/exam-analytics` - 获取数据分析

#### 系统管理
- `GET /api/master-config` - 获取系统配置
- `PUT /api/master-config` - 更新系统配置
- `GET /api/system-status` - 获取系统状态
- `POST /api/test-api` - 测试API连接

## 🗄️ 数据库设计

### 核心表结构

```sql
-- 题库表
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    category VARCHAR(100),
    question_type VARCHAR(20),
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    answer VARCHAR(10),
    explanation TEXT,
    question_id INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);

-- 考试记录表
CREATE TABLE exam_records (
    id VARCHAR(100) PRIMARY KEY,
    user_name VARCHAR(100),
    user_id VARCHAR(100),
    department VARCHAR(100),
    score INTEGER,
    correct_count INTEGER,
    total_questions INTEGER,
    duration INTEGER,
    detailed_answers JSON,
    ai_report TEXT,
    created_at DATETIME
);

-- 系统配置表
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description VARCHAR(500),
    config_type VARCHAR(50),
    updated_at DATETIME
);
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./exam_system.db` |
| `QWEN_API_KEY` | 通义千问API密钥 | 空 |
| `SECRET_KEY` | JWT签名密钥 | `your-secret-key-change-in-production` |

### API配置格式

```json
{
    "provider": "qwen",
    "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "model": "qwen-turbo", 
    "key": "sk-your-api-key",
    "enabled": true
}
```

## 📊 数据分析功能

系统提供丰富的数据分析接口：

- **总体统计**: 考试次数、平均分、优秀率
- **部门分析**: 各部门表现对比
- **时间趋势**: 考试成绩变化趋势
- **个人报告**: AI生成的个性化分析报告

## 🚦 开发指南

### 项目结构
```
python-backend/
├── app/
│   ├── main.py          # 主应用
│   ├── models.py        # 数据库模型
│   ├── schemas.py       # 数据验证模式
│   ├── database.py      # 数据库连接
│   ├── config.py        # 配置管理
│   └── routers/         # API路由
│       ├── questions.py # 题库API
│       ├── exams.py     # 考试API
│       └── admin.py     # 管理API
├── migrate_data.py      # 数据迁移脚本
├── start.py            # 启动脚本
└── requirements.txt    # 依赖列表
```

### 添加新功能

1. **数据模型**: 在 `models.py` 中定义新表
2. **数据验证**: 在 `schemas.py` 中添加验证模式
3. **API路由**: 在 `routers/` 中创建新路由文件
4. **注册路由**: 在 `main.py` 中注册新路由

### 测试API

```bash
# 获取题库
curl http://localhost:8001/api/questions

# 保存考试记录  
curl -X POST http://localhost:8001/api/exam-records \
  -H "Content-Type: application/json" \
  -d '{"id":"test123","userName":"测试用户","score":85,"correctCount":17,"totalQuestions":20,"duration":600}'

# 生成AI报告
curl -X POST http://localhost:8001/api/generate-ai-report \
  -H "Content-Type: application/json" \
  -d '{"exam_record_id":"test123","exam_data":{}}'
```

## 🔒 安全注意事项

1. **生产环境**: 更改默认的 `SECRET_KEY`
2. **数据库**: 使用PostgreSQL等生产级数据库
3. **API密钥**: 妥善保管通义千问API密钥
4. **HTTPS**: 生产环境启用HTTPS
5. **访问控制**: 根据需要添加用户认证

## 📈 性能优化

1. **数据库索引**: 已在关键字段添加索引
2. **连接池**: 使用SQLAlchemy连接池
3. **异步处理**: AI报告生成使用异步调用
4. **缓存**: 可添加Redis缓存热点数据

## 🚀 部署到生产环境

### 使用Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 使用systemd服务

```ini
[Unit]
Description=Exam System API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/python-backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

## ❓ 常见问题

### Q: 如何更换数据库？
A: 修改 `.env` 文件中的 `DATABASE_URL`，安装对应的数据库驱动。

### Q: AI报告生成失败？
A: 检查 `QWEN_API_KEY` 是否正确配置，网络是否能访问通义千问API。

### Q: 如何备份数据？
A: SQLite可直接复制 `.db` 文件，PostgreSQL使用 `pg_dump` 命令。