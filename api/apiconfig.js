// API配置端点 - 自托管API配置
export default async function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // 处理OPTIONS预检请求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    try {
      // 返回API配置
      const apiConfig = {
        "provider": "proxy",
        "url": "https://neurogen-qwen.vercel.app/api/proxy",
        "model": "qwen-turbo",
        "key": process.env.QWEN_API_KEY || "", // 从环境变量读取
        "lastUpdated": new Date().toISOString()
      };
      
      res.status(200).json(apiConfig);
    } catch (error) {
      console.error('API配置错误:', error);
      res.status(500).json({ error: '服务器内部错误' });
    }
  } else {
    res.status(405).json({ error: '不支持的请求方法' });
  }
}