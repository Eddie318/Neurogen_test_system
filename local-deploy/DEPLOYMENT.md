# 穆桥销售测验系统 - 服务器部署指南

## 📦 部署包内容

```
local-clean-version/
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker编排配置
├── nginx.conf             # Nginx服务器配置
├── deploy.sh              # 自动部署脚本
├── exam.html              # 考试系统页面
├── admin.html             # 管理后台页面
├── index.html             # 首页
├── data/                  # 数据目录
│   ├── master-config.json # API配置文件
│   └── master-questions.json # 题库文件(54题)
└── DEPLOYMENT.md          # 本部署说明
```

## 🚀 快速部署

### 方式一：自动部署（推荐）

1. **上传部署包到服务器**
   ```bash
   # 使用scp上传
   scp -r local-clean-version/ root@你的服务器IP:/opt/
   
   # 或使用rsync
   rsync -avz local-clean-version/ root@你的服务器IP:/opt/neurogen-exam/
   ```

2. **执行自动部署**
   ```bash
   cd /opt/local-clean-version  # 或你的上传目录
   sudo bash deploy.sh
   ```

3. **完成！** 脚本会自动：
   - 安装Docker和Docker Compose
   - 配置防火墙
   - 构建和启动服务
   - 显示访问地址

### 方式二：手动部署

1. **准备环境**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y docker.io docker-compose
   
   # CentOS/RHEL
   sudo yum install -y docker docker-compose
   ```

2. **启动服务**
   ```bash
   cd /path/to/local-clean-version
   docker-compose up -d --build
   ```

3. **配置防火墙**
   ```bash
   # Ubuntu (UFW)
   sudo ufw allow 80
   sudo ufw allow 8080
   
   # CentOS (Firewalld)
   sudo firewall-cmd --permanent --add-port=80/tcp
   sudo firewall-cmd --permanent --add-port=8080/tcp
   sudo firewall-cmd --reload
   ```

## 🌐 访问地址

部署成功后，系统将在以下地址可用：

### 主要端口 (80)
- **考试系统**: `http://你的服务器IP/exam.html`
- **销售专用**: `http://你的服务器IP/exam.html?mode=sales`
- **管理后台**: `http://你的服务器IP/admin.html`

### 备用端口 (8080)
- **考试系统**: `http://你的服务器IP:8080/exam.html`
- **销售专用**: `http://你的服务器IP:8080/exam.html?mode=sales`
- **管理后台**: `http://你的服务器IP:8080/admin.html`

## 🔧 管理命令

### 日常运维
```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

### 数据管理
```bash
# 备份数据文件
cp -r data/ /backup/neurogen-$(date +%Y%m%d)/

# 查看磁盘使用
du -sh data/

# 清理Docker镜像
docker system prune -f
```

## ⚙️ 系统配置

### 1. 配置AI分析功能

编辑 `data/master-config.json`:
```json
{
  "version": 2,
  "lastUpdate": "2025-01-22T12:00:00Z",
  "apiConfig": {
    "provider": "qwen",
    "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "model": "qwen-turbo",
    "key": "你的通义千问API密钥",
    "enabled": true
  }
}
```

### 2. 维护题库

编辑 `data/master-questions.json`:
- 添加/修改/删除题目
- 更新版本号
- 重启服务生效

### 3. Nginx配置优化

如需自定义，可编辑 `nginx.conf` 后重新构建：
```bash
docker-compose down
docker-compose up -d --build
```

## 🔒 安全配置

### 1. 防火墙设置
```bash
# 只开放必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # 如果使用HTTPS
sudo ufw enable
```

### 2. SSL证书（可选）

如需HTTPS，可使用Let's Encrypt：
```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d 你的域名

# 修改nginx配置添加SSL
```

### 3. 访问限制

可在nginx配置中添加IP限制：
```nginx
# 限制管理后台访问
location /admin.html {
    allow 192.168.1.0/24;  # 内网IP
    allow 你的办公网IP;
    deny all;
}
```

## 📊 监控和日志

### 1. 系统监控
```bash
# 查看系统资源
docker stats

# 查看端口监听
netstat -tlnp | grep :80

# 查看磁盘空间
df -h
```

### 2. 日志管理
```bash
# 查看nginx访问日志
docker-compose exec neurogen-exam-system tail -f /var/log/nginx/access.log

# 查看错误日志
docker-compose exec neurogen-exam-system tail -f /var/log/nginx/error.log

# 清理旧日志
docker-compose exec neurogen-exam-system logrotate /etc/logrotate.conf
```

## 🚨 故障排除

### 常见问题

**Q: 端口80被占用怎么办？**
```bash
# 查看占用进程
sudo lsof -i :80

# 停止占用进程
sudo systemctl stop apache2  # 或nginx等

# 或使用8080端口访问
```

**Q: Docker镜像构建失败？**
```bash
# 清理旧镜像
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

**Q: 页面无法访问？**
```bash
# 检查服务状态
docker-compose ps

# 检查防火墙
sudo ufw status

# 检查端口监听
netstat -tlnp | grep :80
```

**Q: 数据丢失了？**
```bash
# 检查数据卷挂载
docker-compose config

# 恢复备份
cp -r /backup/neurogen-20250122/data/ ./
docker-compose restart
```

## 🔄 版本更新

### 更新应用
```bash
# 备份当前数据
cp -r data/ /backup/

# 下载新版本
wget 新版本链接 -O new-version.tar.gz
tar -xzf new-version.tar.gz

# 复制数据文件
cp -r /backup/data/ ./new-version/

# 部署新版本
cd new-version
docker-compose down
docker-compose up -d --build
```

## 📞 技术支持

### 联系方式
- 技术问题：提交GitHub Issue
- 紧急支持：联系管理员
- 系统监控：配置告警通知

### 系统要求
- **操作系统**: Linux (Ubuntu 18.04+ / CentOS 7+)
- **内存**: 最低1GB，推荐2GB+
- **磁盘**: 最低10GB可用空间
- **网络**: 公网IP和域名（可选）

### 性能调优
```bash
# 限制容器资源使用
# 在docker-compose.yml中添加：
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

---

**🎉 部署完成后，记得将访问地址分享给你的团队！**

**📱 系统支持手机、平板、电脑等所有设备访问**