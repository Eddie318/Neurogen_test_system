#!/usr/bin/env node

// API功能测试脚本
const http = require('http');

const API_HOST = 'localhost';
const API_PORT = 3001;

// 测试API接口
async function testAPI() {
    console.log('🧪 开始测试API接口...\n');
    
    const tests = [
        {
            name: '获取题库数据',
            path: '/api/master-questions',
            method: 'GET'
        },
        {
            name: '获取配置数据', 
            path: '/api/master-config',
            method: 'GET'
        },
        {
            name: '获取考试记录',
            path: '/api/exam-records',
            method: 'GET'
        },
        {
            name: '通用JSON文件访问 - 题库',
            path: '/api/json?file=master-questions.json',
            method: 'GET'
        },
        {
            name: '通用JSON文件访问 - 配置',
            path: '/api/json?file=master-config.json', 
            method: 'GET'
        }
    ];
    
    for (const test of tests) {
        await runTest(test);
    }
    
    console.log('\n✅ API测试完成！');
}

function runTest(test) {
    return new Promise((resolve) => {
        const options = {
            hostname: API_HOST,
            port: API_PORT,
            path: test.path,
            method: test.method
        };
        
        console.log(`📡 测试: ${test.name}`);
        console.log(`   URL: http://${API_HOST}:${API_PORT}${test.path}`);
        
        const req = http.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    console.log(`   状态: ${res.statusCode}`);
                    
                    if (res.statusCode === 200) {
                        if (jsonData.questions) {
                            console.log(`   ✅ 成功 - 获取到 ${jsonData.questions.length} 道题目`);
                        } else if (jsonData.version) {
                            console.log(`   ✅ 成功 - 配置版本: ${jsonData.version}`);
                        } else if (Array.isArray(jsonData)) {
                            console.log(`   ✅ 成功 - 获取到 ${jsonData.length} 条记录`);
                        } else {
                            console.log('   ✅ 成功 - 数据格式正确');
                        }
                    } else {
                        console.log(`   ❌ 失败 - ${jsonData.message || '未知错误'}`);
                    }
                } catch (error) {
                    console.log(`   ❌ 失败 - JSON解析错误: ${error.message}`);
                }
                console.log('');
                resolve();
            });
        });
        
        req.on('error', (error) => {
            console.log(`   ❌ 连接失败: ${error.message}`);
            console.log('   💡 提示: 请确保API服务器已启动 (node server.js)\n');
            resolve();
        });
        
        req.end();
    });
}

// 检查API服务器是否运行
function checkAPIServer() {
    return new Promise((resolve) => {
        const req = http.request({
            hostname: API_HOST,
            port: API_PORT,
            path: '/api/master-questions',
            method: 'GET',
            timeout: 3000
        }, (res) => {
            console.log('✅ API服务器运行正常\n');
            resolve(true);
        });
        
        req.on('error', () => {
            console.log('❌ API服务器未运行');
            console.log('💡 请先启动API服务器: node server.js\n');
            resolve(false);
        });
        
        req.on('timeout', () => {
            console.log('❌ API服务器响应超时\n');
            resolve(false);
        });
        
        req.end();
    });
}

// 主函数
async function main() {
    console.log('🚀 穆桥销售测验系统 - API测试工具\n');
    
    const serverRunning = await checkAPIServer();
    if (serverRunning) {
        await testAPI();
    } else {
        console.log('⚠️  测试中断：API服务器未运行');
        console.log('');
        console.log('📋 启动步骤:');
        console.log('1. 启动API服务器: node server.js');
        console.log('2. 运行测试: node test-api.js');
    }
}

main().catch(console.error);