#!/usr/bin/env node

/**
 * 考试记录同步服务器
 * 为单文件版本提供数据同步API接口
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const CONFIG = {
    port: 3001,
    dataDir: './sync-data',
    recordsFile: './sync-data/exam-records.json',
    questionsFile: '../local-deploy/data/master-questions.json',
    configFile: '../local-deploy/data/master-config.json'
};

// 确保数据目录存在
if (!fs.existsSync(CONFIG.dataDir)) {
    fs.mkdirSync(CONFIG.dataDir, { recursive: true });
}

/**
 * 读取考试记录
 */
function readExamRecords() {
    try {
        if (fs.existsSync(CONFIG.recordsFile)) {
            const data = fs.readFileSync(CONFIG.recordsFile, 'utf8');
            return JSON.parse(data);
        }
        return [];
    } catch (error) {
        console.error('读取考试记录失败:', error);
        return [];
    }
}

/**
 * 保存考试记录
 */
function saveExamRecords(records) {
    try {
        fs.writeFileSync(CONFIG.recordsFile, JSON.stringify(records, null, 2));
        return true;
    } catch (error) {
        console.error('保存考试记录失败:', error);
        return false;
    }
}

/**
 * 读取题库数据
 */
function readQuestions() {
    try {
        const filePath = path.resolve(__dirname, CONFIG.questionsFile);
        if (fs.existsSync(filePath)) {
            const data = fs.readFileSync(filePath, 'utf8');
            return JSON.parse(data);
        }
        return null;
    } catch (error) {
        console.error('读取题库失败:', error);
        return null;
    }
}

/**
 * 读取配置数据
 */
function readConfig() {
    try {
        const filePath = path.resolve(__dirname, CONFIG.configFile);
        if (fs.existsSync(filePath)) {
            const data = fs.readFileSync(filePath, 'utf8');
            const config = JSON.parse(data);
            // 清空敏感信息
            if (config.apiConfig) {
                config.apiConfig.key = '';
            }
            return config;
        }
        return null;
    } catch (error) {
        console.error('读取配置失败:', error);
        return null;
    }
}

/**
 * 设置CORS头
 */
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

/**
 * 处理API请求
 */
function handleApiRequest(req, res, pathname, query) {
    setCorsHeaders(res);
    
    // 处理OPTIONS请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    console.log(`${new Date().toISOString()} - ${req.method} ${pathname}`);
    
    // 路由处理
    if (pathname === '/api/exam-records') {
        handleExamRecords(req, res);
    } else if (pathname === '/api/master-questions') {
        handleMasterQuestions(req, res);
    } else if (pathname === '/api/master-config') {
        handleMasterConfig(req, res);
    } else if (pathname === '/api/sync-status') {
        handleSyncStatus(req, res);
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            success: false, 
            message: '接口不存在',
            available_endpoints: [
                '/api/exam-records',
                '/api/master-questions', 
                '/api/master-config',
                '/api/sync-status'
            ]
        }));
    }
}

/**
 * 处理考试记录
 */
function handleExamRecords(req, res) {
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
                
                // 检查记录ID是否已存在
                const existingIndex = records.findIndex(r => r.id === newRecord.id);
                if (existingIndex >= 0) {
                    records[existingIndex] = newRecord;
                    console.log(`📝 更新考试记录: ${newRecord.id}`);
                } else {
                    records.push(newRecord);
                    console.log(`📝 新增考试记录: ${newRecord.id} (${newRecord.userName || '匿名'})`);
                }
                
                if (saveExamRecords(records)) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ 
                        success: true, 
                        message: '记录保存成功',
                        totalRecords: records.length
                    }));
                } else {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, message: '记录保存失败' }));
                }
            } catch (error) {
                console.error('处理考试记录失败:', error);
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, message: '数据格式错误' }));
            }
        });
        
    } else {
        res.writeHead(405, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, message: '方法不允许' }));
    }
}

/**
 * 处理题库请求
 */
function handleMasterQuestions(req, res) {
    if (req.method === 'GET') {
        const questions = readQuestions();
        if (questions) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(questions));
        } else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, message: '题库数据不存在' }));
        }
    } else {
        res.writeHead(405, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, message: '方法不允许' }));
    }
}

/**
 * 处理配置请求
 */
function handleMasterConfig(req, res) {
    if (req.method === 'GET') {
        const config = readConfig();
        if (config) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(config));
        } else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, message: '配置数据不存在' }));
        }
    } else {
        res.writeHead(405, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, message: '方法不允许' }));
    }
}

/**
 * 处理同步状态请求
 */
function handleSyncStatus(req, res) {
    const records = readExamRecords();
    const questions = readQuestions();
    const config = readConfig();
    
    const status = {
        server_time: new Date().toISOString(),
        exam_records: {
            total: records.length,
            last_record: records.length > 0 ? records[records.length - 1].timestamp : null
        },
        questions: {
            total: questions ? questions.questions.length : 0,
            version: questions ? questions.version : null,
            last_update: questions ? questions.lastUpdate : null
        },
        config: {
            version: config ? config.version : null
        }
    };
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(status));
}

/**
 * 创建HTTP服务器
 */
const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;
    
    // 处理API请求
    if (pathname.startsWith('/api/')) {
        handleApiRequest(req, res, pathname, query);
    } else {
        // 返回服务器信息
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            service: '穆桥销售测验系统 - 数据同步服务器',
            version: '1.0.0',
            endpoints: [
                'GET /api/exam-records - 获取考试记录',
                'POST /api/exam-records - 保存考试记录',
                'GET /api/master-questions - 获取题库数据',
                'GET /api/master-config - 获取配置数据',
                'GET /api/sync-status - 获取同步状态'
            ],
            usage: '在单文件HTML中使用: ?api=http://this-server-address'
        }));
    }
});

// 启动服务器
server.listen(CONFIG.port, '0.0.0.0', () => {
    console.log('🚀 穆桥销售测验系统 - 数据同步服务器');
    console.log('=====================================');
    console.log(`✅ 服务器启动成功！`);
    console.log(`📡 监听端口: ${CONFIG.port}`);
    console.log(`📁 数据目录: ${CONFIG.dataDir}`);
    console.log('');
    console.log('🌐 API接口:');
    console.log(`   http://localhost:${CONFIG.port}/api/exam-records`);
    console.log(`   http://localhost:${CONFIG.port}/api/master-questions`);
    console.log(`   http://localhost:${CONFIG.port}/api/master-config`);
    console.log(`   http://localhost:${CONFIG.port}/api/sync-status`);
    console.log('');
    console.log('📋 使用方法:');
    console.log(`   在HTML中添加参数: ?api=http://your-server:${CONFIG.port}`);
    console.log('');
    console.log('⌨️  按 Ctrl+C 停止服务器');
    console.log('');
});

// 处理程序退出
process.on('SIGINT', () => {
    console.log('\\n📊 服务器统计:');
    const records = readExamRecords();
    console.log(`   考试记录总数: ${records.length}`);
    console.log('\\n👋 服务器已停止');
    process.exit(0);
});