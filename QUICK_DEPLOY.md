# 穆桥销售测验系统 - 快速部署指南

## 📦 部署包说明

✅ **已生成部署包**: `neurogen-exam-system-20250722.tar.gz`

## 🚀 给开发人员的部署说明

### 1. 上传部署包到服务器

```bash
# 方法1: 使用scp上传
scp neurogen-exam-system-20250722.tar.gz root@服务器IP:/opt/

# 方法2: 直接在服务器上下载
wget 你的文件下载链接 -O neurogen-exam-system.tar.gz
```

### 2. 解压并部署

```bash
# 解压部署包
cd /opt
tar -xzf neurogen-exam-system-20250722.tar.gz
cd neurogen-exam-system/  # 或解压后的目录名

# 一键部署（推荐）
sudo bash deploy.sh
```

### 3. 访问系统

部署成功后访问：
- **考试系统**: `http://服务器IP/exam.html`
- **销售链接**: `http://服务器IP/exam.html?mode=sales` 
- **管理后台**: `http://服务器IP/admin.html`

## 🔧 开发人员备用方案

### 手动部署步骤

```bash
# 1. 安装Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
sudo systemctl enable docker

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 启动服务
docker-compose up -d --build

# 4. 开放防火墙
sudo ufw allow 80
sudo ufw allow 8080
```

### 常用管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

## 🎯 系统特点

✅ **已修复**: 评分系统连接问题  
✅ **已启用**: 答案查看功能  
✅ **已启用**: AI报告生成  
✅ **响应式设计**: 支持手机/平板/电脑  
✅ **完整题库**: 54道专业题目  

## 📞 技术支持

- 遇到问题请查看 `DEPLOYMENT.md` 详细文档
- 系统要求：Linux服务器，1GB+内存，10GB+磁盘
- 支持Ubuntu/CentOS等主流Linux发行版

---

**🎉 部署完成后，任何人都可以通过链接访问考试系统！**