// 题库API端点 - 完全自托管，国内稳定访问
// 包含完整的54道题库，不依赖任何外部服务

import questionBankData from './questionbank_data.json';

const questionBank = questionBankData;

export default async function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // 处理OPTIONS预检请求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    try {
      // 返回题库数据
      res.status(200).json(questionBank);
    } catch (error) {
      console.error('题库API错误:', error);
      res.status(500).json({ error: '服务器内部错误' });
    }
  } else {
    res.status(405).json({ error: '不支持的请求方法' });
  }
}