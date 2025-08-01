const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

// 数据存储文件
const DATA_FILE = path.join(__dirname, 'data', 'exam-records.json');

// 确保数据目录存在
if (!fs.existsSync(path.join(__dirname, 'data'))) {
    fs.mkdirSync(path.join(__dirname, 'data'));
}

// 读取考试记录
function readExamRecords() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            const data = fs.readFileSync(DATA_FILE, 'utf8');
            return JSON.parse(data);
        }
        return [];
    } catch (error) {
        console.error('读取考试记录失败:', error);
        return [];
    }
}

// 保存考试记录
function saveExamRecords(records) {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(records, null, 2));
        return true;
    } catch (error) {
        console.error('保存考试记录失败:', error);
        return false;
    }
}

// 创建HTTP服务器
const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    
    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // 处理OPTIONS请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // API路由
    if (pathname === '/api/exam-records') {
        if (req.method === 'GET') {
            // 获取考试记录
            const records = readExamRecords();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(records));
        } else if (req.method === 'POST') {
            // 添加考试记录
            let body = '';
            req.on('data', chunk => {
                body += chunk.toString();
            });
            req.on('end', () => {
                try {
                    const newRecord = JSON.parse(body);
                    const records = readExamRecords();
                    
                    // 检查是否已存在相同ID的记录
                    const existingIndex = records.findIndex(r => r.id === newRecord.id);
                    if (existingIndex >= 0) {
                        records[existingIndex] = newRecord;
                    } else {
                        records.push(newRecord);
                    }
                    
                    if (saveExamRecords(records)) {
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ success: true, message: '记录保存成功' }));
                    } else {
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ success: false, message: '记录保存失败' }));
                    }
                } catch (error) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, message: '数据格式错误' }));
                }
            });
        } else {
            res.writeHead(405, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, message: '方法不允许' }));
        }
    } else if (pathname === '/api/sync') {
        if (req.method === 'POST') {
            // 同步多条记录
            let body = '';
            req.on('data', chunk => {
                body += chunk.toString();
            });
            req.on('end', () => {
                try {
                    const syncData = JSON.parse(body);
                    const records = readExamRecords();
                    
                    // 合并记录，避免重复
                    syncData.forEach(newRecord => {
                        const existingIndex = records.findIndex(r => r.id === newRecord.id);
                        if (existingIndex >= 0) {
                            records[existingIndex] = newRecord;
                        } else {
                            records.push(newRecord);
                        }
                    });
                    
                    if (saveExamRecords(records)) {
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ 
                            success: true, 
                            message: `成功同步${syncData.length}条记录`,
                            totalRecords: records.length
                        }));
                    } else {
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ success: false, message: '记录同步失败' }));
                    }
                } catch (error) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, message: '数据格式错误' }));
                }
            });
        } else {
            res.writeHead(405, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, message: '方法不允许' }));
        }
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, message: '接口不存在' }));
    }
});

const PORT = 3001;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`数据同步服务器启动在端口 ${PORT}`);
});