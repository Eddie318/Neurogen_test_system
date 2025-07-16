# 通义千问API代理服务器

这是一个部署在Vercel上的代理服务器，用于解决阿里云通义千问API的CORS跨域问题。

## 🚀 快速部署

### 方法1：通过Vercel CLI部署

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
cd vercel-project
vercel --prod
```

### 方法2：通过GitHub部署

1. 将此文件夹推送到GitHub仓库
2. 在Vercel网站导入GitHub项目
3. 自动部署完成

## 📋 部署后配置

1. **获取部署URL**
   - 部署完成后，Vercel会提供一个URL，例如：`https://your-project.vercel.app`

2. **配置考试系统**
   - 打开考试系统后台管理
   - 选择"代理服务器"
   - 将API地址设置为：`https://your-project.vercel.app/api/proxy`
   - 输入您的通义千问API Key
   - 保存配置

## 🔧 API使用方法

代理服务器接收以下格式的POST请求：

```json
{
  "apiKey": "your-qwen-api-key",
  "requestBody": {
    "model": "qwen-turbo",
    "input": {
      "prompt": "你的提示词"
    },
    "parameters": {
      "max_tokens": 1000,
      "temperature": 0.7
    }
  }
}
```

返回通义千问API的原始响应。

## 📁 项目结构

```
vercel-project/
├── api/
│   └── proxy.js          # 代理API端点
├── package.json          # 项目配置
├── vercel.json          # Vercel部署配置
└── README.md            # 说明文档
```

## 🛠️ 本地开发

1. **安装依赖**
```bash
npm install
```

2. **本地运行**
```bash
vercel dev
```

3. **访问本地API**
   - API端点：`http://localhost:3000/api/proxy`

## 🔒 安全说明

- 代理服务器只转发到通义千问官方API
- 不会存储或记录任何API Key
- 支持CORS，但建议在生产环境中限制来源域名

## 📞 故障排除

**常见问题：**

1. **部署失败**
   - 检查Vercel账号配额
   - 确认所有文件路径正确

2. **API调用失败**
   - 验证通义千问API Key是否有效
   - 检查API配额是否充足

3. **CORS错误**
   - 确认代理服务器地址正确
   - 检查浏览器控制台错误信息

## 📝 更新日志

- v1.0.0：初始版本，支持通义千问API代理