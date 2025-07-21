# AI分析功能使用说明

## 支持的AI服务商
本系统支持DeepSeek和通义千问两种AI API，推荐使用DeepSeek。

## 使用步骤

### 1. 配置AI API
1. 打开 `admin.html` 后台管理页面
2. 点击"系统设置"选项卡
3. 点击"加载默认配置"按钮，选择AI服务商
4. 填入相应的API密钥
5. 点击"测试API连接"验证配置
6. 点击"保存配置"

### 2. 获取API密钥

#### DeepSeek（推荐）
- 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
- 注册/登录账号
- 创建API密钥
- **优势：国内直连，稳定快速，无需代理**

#### 通义千问
- 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
- 注册/登录阿里云账号
- 开通DashScope服务
- 创建API密钥

### 3. 使用AI分析
1. 进行考试测试
2. 考试结束后，点击"🤖 生成AI分析报告"按钮
3. 系统会调用AI生成详细的考试分析报告

## 配置格式

### DeepSeek配置（推荐）
```json
{
  "provider": "deepseek",
  "url": "https://api.deepseek.com/chat/completions",
  "model": "deepseek-chat",
  "key": "您的DeepSeek API密钥"
}
```

### 通义千问配置
```json
{
  "provider": "qwen",
  "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  "model": "qwen-turbo",
  "key": "您的通义千问API密钥"
}
```

## 注意事项
1. 推荐使用DeepSeek API，国内访问更稳定
2. API密钥请妥善保管，不要泄露给他人
3. 配置保存在浏览器本地存储中
4. 支持Docker部署，无需额外代理服务

## 故障排除
- **API连接失败**：检查API密钥是否正确
- **网络错误**：检查网络连接或尝试切换API服务商
- **响应异常**：查看控制台错误信息