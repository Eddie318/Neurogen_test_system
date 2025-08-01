# API 基础教程 - 从零开始

## 什么是 API？

API 就像餐厅的"服务员"，帮你在不同的程序之间传递信息。

### 生活中的例子
- **你**：网页（想要数据）
- **厨房**：服务器（有数据）
- **服务员**：API（帮你传递请求和响应）

你不能直接冲进厨房拿菜，必须通过服务员点菜。

## 基本概念

### 1. 请求 (Request) - "点菜"
```javascript
// 就像你对服务员说："我要一份宫保鸡丁"
fetch('/api/exam-records')  // 我要考试记录数据
```

### 2. 响应 (Response) - "上菜"
```javascript
// 服务员把菜端给你
{
  "success": true,
  "data": [
    {"id": "001", "userName": "张三", "score": 85}
  ]
}
```

### 3. HTTP 方法 - "不同的服务方式"
- **GET**：我要看菜单（获取数据）
- **POST**：我要点菜（发送新数据）
- **PUT**：我要换菜（更新数据）
- **DELETE**：我不要这个菜了（删除数据）

## 我们项目中的具体应用

### 问题：考试记录怎么保存？

### 传统方式的问题：
```javascript
// 只能保存在浏览器里，换个电脑就没了
localStorage.setItem('exam-records', JSON.stringify(records));
```

### API 解决方案：
```javascript
// 可以保存到服务器，任何地方都能访问
fetch('/api/exam-records', {
  method: 'POST',
  body: JSON.stringify(examRecord)
});
```

## 我们的 API 接口详解

### 1. 保存考试记录
```javascript
// 相当于："服务员，请帮我保存这份考试记录"
fetch('/api/exam-records', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    id: 'exam_001',
    userName: '张三',
    score: 85,
    timestamp: '2024-01-01 10:00:00'
  })
});

// 服务员回答："好的，已经保存了"
// 响应：{"success": true, "message": "记录保存成功"}
```

### 2. 获取考试记录
```javascript
// 相当于："服务员，给我看看所有的考试记录"
fetch('/api/exam-records')
  .then(response => response.json())
  .then(data => {
    console.log('所有考试记录:', data);
  });

// 服务员回答："这是所有记录"
// 响应：[{记录1}, {记录2}, {记录3}...]
```

### 3. 获取题库数据
```javascript
// 相当于："服务员，给我今天的考试题目"
fetch('/api/master-questions')
  .then(response => response.json())
  .then(questions => {
    console.log('题库:', questions);
  });
```

## sync-server.js 详解

这是我们的"服务员程序"：

```javascript
// 创建一个服务员
const server = http.createServer((req, res) => {
  // 客户来了，看看他要什么
  if (pathname === '/api/exam-records') {
    if (req.method === 'GET') {
      // 客户说："我要看记录"
      const records = readExamRecords();
      res.end(JSON.stringify(records));
    } else if (req.method === 'POST') {
      // 客户说："我要保存记录"
      // 接收数据，保存到文件
      saveExamRecords(newRecord);
      res.end(JSON.stringify({success: true}));
    }
  }
});

// 服务员开始上班，在3001号窗口服务
server.listen(3001);
```

## 实际使用场景

### 场景1：学生做完考试
```javascript
// 1. 学生提交答案
const examResult = {
  userName: '张三',
  score: 85,
  answers: ['A', 'B', 'C', 'D'],
  timestamp: new Date().toISOString()
};

// 2. 发送到服务器保存
fetch('http://your-server:3001/api/exam-records', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(examResult)
})
.then(response => response.json())
.then(result => {
  if (result.success) {
    alert('考试记录已保存！');
  }
});
```

### 场景2：管理员查看记录
```javascript
// 1. 获取所有考试记录
fetch('http://your-server:3001/api/exam-records')
  .then(response => response.json())
  .then(records => {
    // 2. 显示在管理界面
    records.forEach(record => {
      console.log(`${record.userName}: ${record.score}分`);
    });
  });
```

## CORS 是什么？

**跨域问题** - 就像"餐厅规定"

```javascript
// 浏览器："这个客户不是我们餐厅的，不能服务"
// 解决方案：告诉浏览器"可以服务外来客户"
res.setHeader('Access-Control-Allow-Origin', '*');
```

## 常见错误和解决方案

### 1. 连接失败
```
Error: Failed to fetch
```
**原因**：服务器没启动，或者地址错误
**解决**：检查服务器是否运行，地址是否正确

### 2. 跨域错误
```
Access to fetch at 'http://localhost:3001' from origin 'http://localhost' has been blocked by CORS policy
```
**原因**：浏览器安全限制
**解决**：服务器设置CORS头部

### 3. 数据格式错误
```
Unexpected token < in JSON
```
**原因**：服务器返回的不是JSON格式
**解决**：检查服务器响应内容

## 测试 API 的方法

### 1. 浏览器直接访问（只能测试GET）
```
http://localhost:3001/api/exam-records
```

### 2. 使用 curl 命令
```bash
# 获取数据
curl http://localhost:3001/api/exam-records

# 发送数据
curl -X POST http://localhost:3001/api/exam-records \
  -H "Content-Type: application/json" \
  -d '{"userName":"测试","score":90}'
```

### 3. 在网页控制台测试
```javascript
// 按F12打开控制台，粘贴这些代码测试
fetch('/api/exam-records')
  .then(r => r.json())
  .then(data => console.log(data));
```

## 为什么要用 API？

### 优点：
1. **数据共享**：多个网页可以共享同一份数据
2. **数据持久化**：数据保存在服务器，不会丢失
3. **统一管理**：所有数据操作都通过API，便于管理
4. **安全性**：可以控制谁能访问什么数据

### 缺点：
1. **复杂性**：需要额外的服务器程序
2. **网络依赖**：需要网络连接才能使用

## 下一步学习建议

1. **先理解概念**：API就是程序之间的"传话筒"
2. **动手测试**：启动我们的sync-server.js，用浏览器访问试试
3. **查看网络**：按F12看网络请求，观察数据传输
4. **修改代码**：尝试添加新的API接口

记住：**API 就是让不同程序互相"说话"的桥梁，不要想得太复杂！**