# 🚀 医学考试系统 - Vercel部署指南

## 📋 项目概述

项目已准备好部署，包含两个独立的Vercel项目：

1. **主应用** (`neurogen-exam-system/`) - 考试系统前端
2. **代理服务器** (`qwen-proxy/`) - 解决CORS问题的API代理

## 🎯 部署步骤

### 第一步：部署代理服务器 (可选但推荐)

```bash
# 进入代理服务器目录
cd qwen-proxy

# 登录Vercel (选择GitHub登录推荐)
vercel login

# 部署代理服务器
vercel --prod

# 记录返回的URL，例如：https://qwen-proxy-abc123.vercel.app
```

### 第二步：部署主应用

```bash
# 进入主应用目录  
cd ../neurogen-exam-system

# 部署主应用
vercel --prod

# 记录返回的URL，例如：https://neurogen-exam-system-xyz789.vercel.app
```

## 🔧 部署后配置

### 1. 访问系统
- **主页**: `https://your-main-app.vercel.app`
- **考试系统**: `https://your-main-app.vercel.app/exam`
- **后台管理**: `https://your-main-app.vercel.app/admin`

### 2. 配置API服务

打开后台管理页面，进行以下配置：

#### 方案A：使用代理服务器 (推荐)
- **API服务商**: 代理服务器
- **API地址**: `https://your-proxy.vercel.app/api/proxy`
- **API Key**: 你的通义千问API Key
- **模型名称**: `qwen-turbo`

#### 方案B：使用Google Gemini (无需代理)
- **API服务商**: Google Gemini  
- **API地址**: `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent`
- **API Key**: 从 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取
- **模型名称**: `gemini-1.5-flash`

#### 方案C：使用OpenAI (无需代理)
- **API服务商**: OpenAI
- **API地址**: `https://api.openai.com/v1/chat/completions`
- **API Key**: 你的OpenAI API Key
- **模型名称**: `gpt-3.5-turbo`

### 3. 导入题库

1. 准备Excel文件，格式如下：

| 列A | 列B | 列C | 列D | 列E | 列F | 列G | 列H |
|-----|-----|-----|-----|-----|-----|-----|-----|
| 题目类别 | 题目类型 | 题目内容 | 正确答案 | 选项A | 选项B | 选项C | 选项D |

2. 在后台管理中点击"📤 批量导入"
3. 上传Excel文件
4. 等待导入完成

## 📁 项目文件结构

```
Neurogen_sales_test/
├── neurogen-exam-system/          # 主应用 (部署到Vercel)
│   ├── index.html                 # 首页
│   ├── admin.html                 # 后台管理
│   ├── exam.html                  # 考试系统
│   ├── package.json               # 项目配置
│   ├── vercel.json                # Vercel配置
│   └── README.md                  # 说明文档
│
├── qwen-proxy/                    # 代理服务器 (部署到Vercel)
│   ├── api/
│   │   └── proxy.js               # 代理API
│   ├── package.json               # 项目配置
│   ├── vercel.json                # Vercel配置
│   └── README.md                  # 说明文档
│
├── cors-proxy.html                # CORS解决方案说明
├── vercel-proxy-example.js        # 代理服务器示例
├── 使用指南.md                     # 详细使用文档
└── DEPLOYMENT.md                  # 本部署指南
```

## 🔄 GitHub自动部署 (推荐)

### 1. 推送到GitHub

```bash
# 初始化git仓库
git init
git add .
git commit -m "医学考试系统 - 初始提交"

# 推送到GitHub
git remote add origin https://github.com/your-username/neurogen-exam-system.git
git push -u origin main
```

### 2. 在Vercel中导入

1. 访问 [Vercel](https://vercel.com)
2. 点击 "Import Project"
3. 连接GitHub账户
4. 选择项目仓库
5. 分别导入两个子目录：
   - `neurogen-exam-system` → 主应用
   - `qwen-proxy` → 代理服务器

## 📊 测试部署

### 1. 功能测试清单

- [ ] 访问主页显示正常
- [ ] 后台管理页面可以打开
- [ ] 考试系统页面可以打开
- [ ] API配置保存成功
- [ ] Excel导入功能正常
- [ ] 考试流程完整可用
- [ ] AI报告生成正常
- [ ] 移动端显示正常

### 2. 代理服务器测试

```bash
# 测试代理API
curl -X POST https://your-proxy.vercel.app/api/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "your-qwen-api-key",
    "requestBody": {
      "model": "qwen-turbo",
      "input": {
        "prompt": "你好"
      },
      "parameters": {
        "max_tokens": 100
      }
    }
  }'
```

## 🎉 部署完成

恭喜！你的医学考试系统已成功部署到Vercel。

### 下一步
1. 配置API服务
2. 导入题库
3. 测试考试流程
4. 分享给用户使用

### 获取API Key
- **Google Gemini**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **通义千问**: [阿里云控制台](https://dashscope.console.aliyun.com/)
- **智谱AI**: [智谱AI开放平台](https://open.bigmodel.cn/)

## 📞 支持

如有问题，请检查：
1. Vercel部署日志
2. 浏览器控制台错误
3. API配置是否正确
4. 网络连接是否正常