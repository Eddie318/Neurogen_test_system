# 穆桥销售测验系统 - 单文件部署版本

## 🎯 **完美解决你的需求**

**只有一个外部服务器地址？没问题！** 这个版本只需要一个 `exam-standalone.html` 文件就能运行完整的考试系统。

## 🚀 **核心特性**

✅ **单文件自包含** - 无需任何外部依赖文件  
✅ **内嵌完整题库** - 54道专业题目直接内置  
✅ **内嵌系统配置** - 所有配置数据内置  
✅ **外部API同步** - 可选连接外部数据服务器  
✅ **本地数据存储** - 考试记录保存在浏览器  
✅ **管理后台优先** - 默认显示管理入口界面  

## 📁 **文件结构**

```
single-file-deploy/
├── exam-standalone.html    # 🌟 唯一需要的文件
└── README-SINGLE-FILE.md   # 使用说明
```

## 🌐 **部署方式**

### 方式1: 纯静态部署（推荐）
```bash
# 只需上传一个文件到任何静态服务器
scp exam-standalone.html user@server:/var/www/html/
```

访问地址：
- **管理入口**: `http://your-server.com/exam-standalone.html`
- **销售考试**: `http://your-server.com/exam-standalone.html?mode=sales`

### 方式2: 外部API同步
```bash
# 如果你有独立的API服务器
http://your-server.com/exam-standalone.html?api=http://api-server.com
```

## 💡 **使用场景**

### 🎯 **你的场景：只有一个地址**
```
✅ 外部服务器只能部署静态文件
✅ 没有Node.js/Docker环境
✅ 需要完整的考试功能
✅ 要求管理员优先界面
```

### 📊 **工作原理**

**数据获取优先级**：
1. **内嵌数据**（第一优先级）- 54道题目 + 配置
2. **外部API**（第二优先级）- 可选同步服务器
3. **本地存储**（兜底方案）- localStorage

**考试记录保存**：
1. **本地存储** - 始终保存在浏览器
2. **外部API** - 可选同步到远程服务器

## 🎨 **界面设计**

### 管理员访问 (`exam-standalone.html`)
```
┌─────────────────────────────┐
│        系统管理             │
├─────────────────────────────┤
│ 🔧 进入管理后台             │
│ 📝 开始考试                │
│ 📋 销售链接复制             │
│ 🌐 外部API状态显示          │
└─────────────────────────────┘
```

### 销售人员访问 (`?mode=sales`)
```
┌─────────────────────────────┐
│      直接进入考试           │
├─────────────────────────────┤
│ 考试界面                   │
│ (无管理功能)                │
└─────────────────────────────┘
```

## 🔧 **高级功能**

### 外部API同步
```javascript
// URL参数配置
http://your-server.com/exam-standalone.html?api=http://api-server.com

// 自动同步功能
- 获取题库数据: GET /api/master-questions
- 获取配置数据: GET /api/master-config  
- 保存考试记录: POST /api/exam-records
```

### 本地数据管理
```javascript
// 浏览器控制台操作
localStorage.getItem('examRecords')      // 查看考试记录
localStorage.getItem('apiConfig')        // 查看API配置
localStorage.clear()                     // 清空所有数据
```

## 📊 **数据说明**

### 内嵌题库
- **题目数量**: 54道专业题目
- **题目类型**: 单选题 + 多选题
- **分类标签**: 疾病、指南、ASM、开浦兰、维派特、优普洛
- **每题包含**: 题号、分类、题目、选项、答案、解析

### 考试配置
- **考试时长**: 30分钟
- **题目数量**: 5道随机题目
- **及格分数**: 60分
- **AI报告**: 内置提示词（需外部API支持）

## 🛡️ **安全特性**

✅ **无敏感数据泄露** - API密钥默认清空  
✅ **销售模式保护** - 自动移除答案和解析  
✅ **跨域安全** - 支持CORS配置  
✅ **数据验证** - 输入数据自动验证  

## 🚀 **性能优化**

- **单文件加载** - 减少HTTP请求
- **内嵌数据** - 无网络延迟
- **智能缓存** - localStorage优化
- **响应式设计** - 移动端适配

## 🔍 **故障排除**

### 常见问题

**Q: 题库显示0道题目？**
```
A: 检查浏览器控制台，确认内嵌数据加载正常
   打开F12 → Console → 查看是否有JavaScript错误
```

**Q: 外部API连接失败？**
```
A: 检查API服务器地址和CORS配置
   确保API服务器支持跨域请求
```

**Q: 考试记录丢失？**
```
A: 考试记录保存在浏览器localStorage中
   清理浏览器数据会导致记录丢失
   建议定期备份或使用外部API同步
```

**Q: AI报告无法生成？**
```
A: AI功能需要外部API支持
   检查API配置或使用内置的本地分析报告
```

## 📋 **使用检查清单**

### 部署前
- [ ] 确认服务器支持HTML静态文件
- [ ] 测试文件上传和访问权限
- [ ] 确认域名和SSL证书（推荐）

### 部署后  
- [ ] 访问管理入口测试基本功能
- [ ] 测试销售链接是否正常工作
- [ ] 检查考试记录保存功能
- [ ] 验证外部API同步（如果使用）

### 运营中
- [ ] 定期备份考试记录数据
- [ ] 监控系统访问和使用情况
- [ ] 根据需要更新题库内容
- [ ] 保持API服务器稳定运行

## 🎉 **使用示例**

### 基础使用
```bash
# 1. 上传文件到服务器
scp exam-standalone.html user@server:/var/www/html/

# 2. 访问管理界面
https://your-domain.com/exam-standalone.html

# 3. 复制销售链接
https://your-domain.com/exam-standalone.html?mode=sales
```

### 高级使用
```bash
# 连接外部API服务器
https://your-domain.com/exam-standalone.html?api=https://api.company.com

# 销售模式 + 外部API
https://your-domain.com/exam-standalone.html?mode=sales&api=https://api.company.com
```

---

## 🎯 **完美匹配你的需求**

✅ **单地址部署** - 只需要一个exam-standalone.html  
✅ **完整功能** - 考试、管理、AI报告全支持  
✅ **管理优先** - 默认显示管理后台入口  
✅ **灵活扩展** - 可选外部API同步  
✅ **即上即用** - 上传文件立即可用  

**这就是你需要的完美解决方案！** 🚀