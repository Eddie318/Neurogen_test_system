// 通义千问API代理服务器
// 解决CORS跨域问题

export default async function handler(req, res) {
  // 设置CORS头，允许所有来源访问
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  res.setHeader('Access-Control-Max-Age', '86400'); // 24小时

  // 处理OPTIONS预检请求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // 只允许POST请求
  if (req.method !== 'POST') {
    res.status(405).json({ 
      error: 'Method Not Allowed',
      message: '只支持POST请求' 
    });
    return;
  }

  try {
    // 验证请求体
    if (!req.body) {
      res.status(400).json({
        error: 'Bad Request',
        message: '请求体不能为空'
      });
      return;
    }

    const { apiKey, requestBody } = req.body;
    
    // 验证必需参数
    if (!apiKey) {
      res.status(400).json({
        error: 'Bad Request',
        message: '缺少API Key'
      });
      return;
    }

    if (!requestBody) {
      res.status(400).json({
        error: 'Bad Request',
        message: '缺少请求体'
      });
      return;
    }

    console.log('收到代理请求，模型:', requestBody.model);

    // 构建通义千问API请求
    const apiResponse = await fetch('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'X-DashScope-SSE': 'disable'
      },
      body: JSON.stringify(requestBody)
    });

    // 检查API响应
    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      console.error('通义千问API错误:', apiResponse.status, errorText);
      
      res.status(apiResponse.status).json({
        error: 'API Error',
        message: `通义千问API调用失败: ${apiResponse.status}`,
        details: errorText
      });
      return;
    }

    // 解析API响应
    const data = await apiResponse.json();
    
    // 验证响应格式
    if (!data.output || !data.output.text) {
      console.error('通义千问API响应格式异常:', data);
      res.status(500).json({
        error: 'Invalid Response',
        message: 'API响应格式不正确',
        response: data
      });
      return;
    }

    console.log('代理请求成功，返回结果长度:', data.output.text.length);

    // 返回成功响应
    res.status(200).json(data);

  } catch (error) {
    console.error('代理服务器错误:', error);
    
    // 处理网络错误
    if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      res.status(503).json({
        error: 'Service Unavailable',
        message: '无法连接到通义千问API服务'
      });
      return;
    }

    // 处理超时错误
    if (error.code === 'ETIMEDOUT') {
      res.status(504).json({
        error: 'Gateway Timeout',
        message: 'API请求超时'
      });
      return;
    }

    // 处理其他错误
    res.status(500).json({
      error: 'Internal Server Error',
      message: `代理服务器内部错误: ${error.message}`
    });
  }
}