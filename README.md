# 穆桥销售测验系统

## 📖 项目简介

穆桥销售测验系统是一个专为销售团队设计的在线考试平台，支持题库管理、考试记录、AI智能分析等功能。系统采用前端技术栈，基于localStorage数据存储，支持Docker一键部署。

## ✨ 核心功能

### 🎯 题库管理
- **题目类型**：支持单选题和多选题
- **分类管理**：疾病、指南、ASM、开浦兰、维派特、优普洛等
- **批量导入**：支持Excel文件批量导入题库
- **在线编辑**：支持题目的增删改查操作
- **内置题库**：预装54道专业题目

### 📝 考试系统
- **随机抽题**：从题库中随机选择15道题目
- **限时考试**：30分钟考试时限，实时倒计时
- **即时评分**：考试结束自动计算分数和正确率
- **答题记录**：保存详细的答题过程和结果
- **响应式设计**：完美支持手机、平板、电脑访问

### 📊 考试记录管理
- **记录查看**：按时间、姓名、分数筛选考试记录
- **详情展示**：查看每道题的详细答题情况
- **数据导出**：支持CSV格式导出所有考试记录
- **统计分析**：总次数、平均分、及格率等统计信息
- **智能清理**：按时间清理历史记录，防止存储溢出

### 🤖 AI智能分析
- **支持API**：通义千问（推荐）、DeepSeek
- **智能评估**：基于考试结果生成个性化学习建议
- **专业报告**：针对销售人员的专业知识点分析
- **一键生成**：考试完成后一键生成AI分析报告

### 🔐 双模式设计
- **管理员模式**：完整的后台管理功能
- **销售模式**：隐藏管理功能，专注考试体验
- **权限控制**：通过URL参数控制访问权限

### 💾 存储管理
- **使用监控**：实时监控localStorage使用情况
- **智能预警**：存储空间不足时自动提醒
- **自动清理**：按时间策略清理旧记录
- **数据备份**：支持数据导出备份

## 🏗️ 技术架构

### 前端技术
- **HTML5 + CSS3**：响应式布局，支持移动端
- **Vanilla JavaScript**：原生JS，无框架依赖
- **SheetJS**：Excel文件解析和处理
- **localStorage**：本地数据存储

### 部署技术
- **Docker**：容器化部署
- **Nginx**：静态文件服务和反向代理
- **跨平台**：支持Windows、Linux、macOS

## 📁 项目结构

```
local-clean-version/
├── admin.html              # 后台管理主页面
├── exam.html               # 考试系统主页面
├── index.html              # 项目首页
├── excel-import.js         # Excel导入功能
├── initial-questions.json  # 初始题库数据(54题)
├── 404.html               # 404错误页面
├── 50x.html               # 服务器错误页面
├── Dockerfile             # Docker镜像构建文件
├── docker-compose.yml     # Docker编排文件
├── nginx.conf             # Nginx配置文件
├── .dockerignore          # Docker忽略文件
├── start.sh               # Linux/Mac启动脚本
├── start.bat              # Windows启动脚本
├── 使用说明.md            # 系统使用说明
├── 部署说明.md            # 详细部署文档
└── AI分析功能使用说明.md   # AI功能配置说明
```

## 🚀 快速部署

### 方式一：一键脚本部署（推荐）

**Windows用户：**
```bash
# 双击运行
start.bat
```

**Linux/Mac用户：**
```bash
# 进入项目目录
cd local-clean-version

# 运行启动脚本
./start.sh
```

### 方式二：手动Docker部署

```bash
# 1. 进入项目目录
cd local-clean-version

# 2. 使用docker-compose启动
docker-compose up -d

# 3. 查看状态
docker-compose ps
```

### 方式三：原生Docker命令

```bash
# 1. 构建镜像
docker build -t neurogen-exam-system .

# 2. 运行容器
docker run -d --name neurogen-exam-system -p 80:80 neurogen-exam-system
```

## 🌐 访问地址

部署完成后，可通过以下地址访问：

- **后台管理**：http://您的IP/admin.html
- **考试系统**：http://您的IP/exam.html
- **销售专用链接**：http://您的IP/exam.html?mode=sales

> 💡 将`您的IP`替换为实际的服务器IP地址，本地部署使用`localhost`

## ⚙️ 初始配置

### 1. 配置AI分析功能

1. 访问后台管理 → 系统设置
2. 点击"加载默认配置"
3. 选择"通义千问（推荐）"
4. 填入您的API密钥
5. 测试连接并保存

> 📝 API密钥获取：访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)

### 2. 导入题库（可选）

- 系统已内置54道专业题目
- 支持Excel格式批量导入
- 可在后台管理中添加、编辑题目

### 3. 分享销售链接

将以下链接分享给销售人员：
```
http://您的IP/exam.html?mode=sales
```

## 📱 移动端支持

系统采用响应式设计，完美支持：
- 📱 手机浏览器（iOS Safari、Android Chrome）
- 📟 平板设备
- 💻 桌面浏览器
- 🧭 微信内置浏览器

## 🔧 管理维护

### 常用Docker命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新重建
docker-compose down && docker-compose up -d --build
```

### 数据管理

- **考试记录**：在后台管理 → 考试记录中查看和管理
- **存储监控**：点击"存储使用情况"查看详细信息
- **数据备份**：定期使用"导出记录"功能备份数据
- **清理维护**：当存储不足时使用"清理旧记录"功能

## 📋 功能详情

### 后台管理功能
- ✅ 题库管理（增删改查、分类）
- ✅ 批量导入（Excel支持）
- ✅ 考试记录（查看、筛选、导出）
- ✅ 系统设置（AI API配置）
- ✅ 存储管理（监控、清理）
- ✅ 数据导出（CSV格式）

### 考试系统功能
- ✅ 用户信息（姓名输入）
- ✅ 随机抽题（15题/次）
- ✅ 限时考试（30分钟）
- ✅ 实时答题（支持修改）
- ✅ 自动评分（分数+正确率）
- ✅ AI分析报告（智能生成）

### 销售模式功能
- ✅ 简化界面（隐藏管理入口）
- ✅ 专注考试体验
- ✅ 自动记录成绩
- ✅ 移动端优化

## 🛠️ 故障排除

### 常见问题

**Q: 容器启动失败？**
A: 检查端口占用，运行 `netstat -tulpn | grep :80`

**Q: 页面无法访问？**
A: 检查防火墙设置，确认端口80已开放

**Q: AI分析功能不可用？**
A: 检查API密钥配置，确认网络连接正常

**Q: 考试记录丢失？**
A: 数据存储在浏览器localStorage，清除浏览器数据会丢失记录

### 技术支持

如遇问题，请按以下顺序检查：
1. Docker服务是否正常运行
2. 端口是否被占用
3. 防火墙设置是否正确
4. 浏览器控制台是否有错误信息

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目的支持：
- [SheetJS](https://sheetjs.com/) - Excel文件处理
- [Nginx](https://nginx.org/) - 高性能Web服务器
- [Docker](https://www.docker.com/) - 容器化平台

---

**🚀 立即开始使用，为您的销售团队提供专业的知识测评平台！**