# 医学考试系统

智能化医学知识测评平台，支持题库管理、智能考试和AI评估报告。

## 🚀 部署到Vercel

### 方法1：通过Vercel CLI

1. **安装Vercel CLI**
```bash
npm install -g vercel
```

2. **登录Vercel**
```bash
vercel login
```

3. **部署项目**
```bash
vercel --prod
```

### 方法2：通过GitHub

1. 将项目推送到GitHub
2. 在Vercel网站导入GitHub项目
3. 自动部署完成

## 📋 系统功能

### 🎯 前台考试系统 (`exam.html`)
- 智能随机抽题
- 实时答题反馈
- 进度跟踪显示
- AI生成学习报告
- 移动端适配

### 🔧 后台管理系统 (`admin.html`)
- 题库CRUD管理
- Excel批量导入
- API配置管理
- 数据统计分析
- 导入历史记录

## ⚙️ 使用步骤

1. **首次配置**
   - 访问 `/admin.html` 进入后台管理
   - 配置AI服务API (OpenAI/通义千问/智谱AI)
   - 导入Excel格式题库

2. **开始考试**
   - 访问 `/exam.html` 进入考试界面
   - 系统自动从题库随机选题
   - 完成后查看AI评估报告

## 📊 Excel题库格式

| 列A | 列B | 列C | 列D | 列E | 列F | 列G | 列H |
|-----|-----|-----|-----|-----|-----|-----|-----|
| 题目类别 | 题目类型 | 题目内容 | 正确答案 | 选项A | 选项B | 选项C | 选项D |
| 疾病 | 单选题 | 题目描述... | A | 选项A内容 | 选项B内容 | 选项C内容 | 选项D内容 |

## 🔧 API配置

### 支持的AI服务
- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`
- **通义千问**: `qwen-turbo`, `qwen-plus` 
- **智谱AI**: `glm-4`
- **Google Gemini**: `gemini-1.5-flash`, `gemini-pro`

### CORS解决方案
- 通义千问和智谱AI需要代理服务器
- 建议部署代理服务器或使用支持CORS的API

## 📱 技术特性

- ✅ 响应式设计，移动端友好
- ✅ 本地存储，无需数据库
- ✅ 支持多种AI服务
- ✅ Excel批量导入
- ✅ 实时数据同步
- ✅ 错误恢复机制

## 🛠️ 项目结构

```
neurogen-exam-system/
├── index.html          # 首页导航
├── admin.html          # 后台管理系统
├── exam.html           # 前台考试系统
├── package.json        # 项目配置
├── vercel.json         # Vercel部署配置
└── README.md           # 说明文档
```

## 📞 支持与帮助

- 浏览器要求：Chrome/Firefox/Safari/Edge (近3年版本)
- JavaScript和localStorage支持
- 网络连接 (用于AI功能)

---

部署完成后访问：
- 🏠 首页：`https://your-project.vercel.app`
- 🎯 考试：`https://your-project.vercel.app/exam`
- 🔧 管理：`https://your-project.vercel.app/admin`