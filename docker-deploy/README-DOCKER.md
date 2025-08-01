# 穆桥销售测验系统 - Docker部署版本

## 📦 概述

这是专为Docker容器部署设计的版本，解决了静态文件访问限制的问题。通过API方式提供JSON数据，确保在容器环境中正常运行。

## 🚀 快速启动

### 1. 一键启动
```bash
./docker-start.sh
```

### 2. 手动启动
```bash
# 构建并启动服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

## 🌐 访问地址

- **考试系统**: http://localhost/exam.html
- **销售链接**: http://localhost/exam.html?mode=sales  
- **管理后台**: http://localhost/admin.html

## 🔧 架构说明

### 服务组件
1. **neurogen-web** (端口 80): Nginx Web服务器
2. **neurogen-api** (端口 3001): Node.js API服务器

### API接口
- `GET /api/master-questions` - 获取题库数据
- `GET /api/master-config` - 获取配置数据
- `GET /api/exam-records` - 获取考试记录
- `POST /api/exam-records` - 保存考试记录
- `GET /api/json?file=xxx.json` - 通用JSON文件访问

### 自动切换
系统会自动检测运行环境：
- 非localhost环境自动使用API模式
- 可通过 `?api=true` 参数强制启用API模式

## 📁 文件结构

```
docker-deploy/
├── admin.html              # 管理后台
├── exam.html               # 考试系统
├── index.html              # 首页
├── server.js               # Node.js API服务器
├── Dockerfile              # Web服务镜像
├── Dockerfile.api          # API服务镜像
├── docker-compose.yml      # 容器编排配置
├── docker-start.sh         # 一键启动脚本
├── nginx.conf              # Nginx配置
└── data/                   # 数据目录
    ├── master-questions.json
    ├── master-config.json
    └── exam-records.json
```

## 🛠️ 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 强制重建
docker-compose up --build --force-recreate
```

## 📊 与本地部署的区别

| 功能 | 本地部署 | Docker部署 |
|------|----------|------------|
| 数据访问 | 直接访问JSON文件 | 通过API接口 |
| 服务架构 | Python HTTP + Node.js | Nginx + Node.js |
| 部署方式 | 手动脚本 | Docker容器 |
| 扩展性 | 单机 | 容器化，易扩展 |

## ⚡ 性能优化

- 使用Alpine Linux基础镜像
- Nginx反向代理优化
- 健康检查机制
- 数据持久化存储

## 🔐 安全特性

- API接口访问控制
- 文件访问白名单
- 容器网络隔离
- 数据卷权限控制

## 📝 注意事项

1. 确保Docker和Docker Compose已安装
2. data目录需要读写权限
3. 端口80和3001需要可用
4. 首次启动需要较长时间构建镜像

## 🆘 故障排除

### 端口冲突
```bash
# 修改docker-compose.yml中的端口映射
ports:
  - "8080:80"  # Web端口
  - "3002:3001"  # API端口
```

### 数据权限问题
```bash
# 设置数据目录权限
chmod -R 755 data/
```

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs
```