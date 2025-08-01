# 穆桥销售测验系统

## 📁 文件结构

```
local-clean-version/
├── admin.html              # 后台管理（只读查看）
├── exam.html               # 考试系统
├── index.html              # 系统首页  
├── simple-start.sh         # 启动脚本
├── stop.sh                 # 停止脚本
├── data/
│   ├── master-config.json  # API配置文件
│   └── master-questions.json # 题库文件（54道题）
└── README.md               # 本说明文件
```

## 🚀 快速启动

```bash
# 启动系统
./simple-start.sh

# 访问地址
http://localhost:8000/admin.html           # 后台管理
http://localhost:8000/exam.html?mode=sales # 销售测试
```

## 🔧 维护方式

### 修改配置
编辑 `data/master-config.json` - 修改通义千问API配置

### 维护题库  
编辑 `data/master-questions.json` - 添加/修改/删除题目

### 应用更新
```bash
./stop.sh
./simple-start.sh
```

## 🎯 系统特点

- ✅ **线下维护** - 只需编辑JSON文件
- ✅ **权限分离** - 销售端看不到答案
- ✅ **自动加载** - 每次打开自动同步最新数据
- ✅ **移动友好** - 支持手机访问
- ✅ **AI分析** - 通义千问智能报告

## 📱 移动端访问

将localhost替换为本机IP即可：
```
http://192.168.x.x:8000/exam.html?mode=sales
```

---

**🎉 系统已优化为最简洁的架构，只保留核心功能！**