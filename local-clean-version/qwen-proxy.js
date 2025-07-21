const http = require('http');
const https = require('https');
const url = require('url');

const PORT = 3001;
const QWEN_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation';

const server = http.createServer((req, res) => {
    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // 处理预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    if (req.method === 'POST' && req.url === '/api/qwen') {
        let body = '';
        
        req.on('data', chunk => {
            body += chunk.toString();
        });

        req.on('end', () => {
            try {
                const requestData = JSON.parse(body);
                const apiKey = requestData.apiKey;
                const requestBody = requestData.requestBody;

                if (!apiKey || !requestBody) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: '缺少apiKey或requestBody' }));
                    return;
                }

                // 转发请求到通义千问API
                const options = {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    }
                };

                const proxyReq = https.request(QWEN_API_URL, options, (proxyRes) => {
                    let responseData = '';

                    proxyRes.on('data', chunk => {
                        responseData += chunk;
                    });

                    proxyRes.on('end', () => {
                        res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json' });
                        res.end(responseData);
                    });
                });

                proxyReq.on('error', (error) => {
                    console.error('代理请求错误:', error);
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: '代理请求失败: ' + error.message }));
                });

                proxyReq.write(JSON.stringify(requestBody));
                proxyReq.end();

            } catch (error) {
                console.error('请求解析错误:', error);
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: '请求格式错误: ' + error.message }));
            }
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '接口不存在' }));
    }
});

server.listen(PORT, () => {
    console.log(`通义千问代理服务已启动，端口: ${PORT}`);
    console.log(`API地址: http://localhost:${PORT}/api/qwen`);
    console.log(`请在后台管理中配置URL为: http://localhost:${PORT}/api/qwen`);
});