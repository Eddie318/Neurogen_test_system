#!/usr/bin/env node

/**
 * 题库更新工具
 * 用于更新单文件版本中的内嵌题库数据
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
    sourceFile: '../local-deploy/data/master-questions.json',  // 源题库文件
    targetFile: './exam-standalone.html',                      // 目标HTML文件
    backupSuffix: '.backup.' + new Date().toISOString().slice(0,19).replace(/:/g, '-')
};

/**
 * 主函数
 */
async function main() {
    console.log('🔄 穆桥销售测验系统 - 题库更新工具');
    console.log('=====================================');
    
    try {
        // 1. 读取新题库数据
        console.log('📖 读取新题库数据...');
        const newQuestions = readNewQuestions();
        console.log(`✅ 读取到 ${newQuestions.questions.length} 道题目`);
        
        // 2. 备份现有文件
        console.log('💾 备份现有文件...');
        backupCurrentFile();
        console.log('✅ 备份完成');
        
        // 3. 更新HTML文件
        console.log('🔧 更新HTML文件中的题库数据...');
        updateHtmlFile(newQuestions);
        console.log('✅ 题库更新完成');
        
        // 4. 验证更新结果
        console.log('🧪 验证更新结果...');
        verifyUpdate();
        console.log('✅ 验证通过');
        
        console.log('');
        console.log('🎉 题库更新成功完成！');
        console.log('');
        console.log('📋 后续步骤：');
        console.log('1. 测试更新后的HTML文件');
        console.log('2. 重新部署到服务器');
        console.log('3. 如需Docker部署，运行: ./deploy-single.sh');
        
    } catch (error) {
        console.error('❌ 更新失败:', error.message);
        console.log('');
        console.log('🔄 回滚说明：');
        console.log(`如需回滚，请执行:`);
        console.log(`cp ${CONFIG.targetFile}${CONFIG.backupSuffix} ${CONFIG.targetFile}`);
        process.exit(1);
    }
}

/**
 * 读取新题库数据
 */
function readNewQuestions() {
    const filePath = path.resolve(__dirname, CONFIG.sourceFile);
    
    if (!fs.existsSync(filePath)) {
        throw new Error(`源题库文件不存在: ${filePath}`);
    }
    
    const content = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(content);
    
    // 验证数据格式
    if (!data.questions || !Array.isArray(data.questions)) {
        throw new Error('题库数据格式不正确：缺少questions数组');
    }
    
    if (data.questions.length === 0) {
        throw new Error('题库为空');
    }
    
    // 验证题目格式
    data.questions.forEach((q, index) => {
        const required = ['question', 'optionA', 'optionB', 'optionC', 'optionD', 'answer', 'category', 'type'];
        for (const field of required) {
            if (!q[field]) {
                throw new Error(`第${index + 1}题缺少必需字段: ${field}`);
            }
        }
    });
    
    return data;
}

/**
 * 备份现有文件
 */
function backupCurrentFile() {
    const targetPath = path.resolve(__dirname, CONFIG.targetFile);
    const backupPath = targetPath + CONFIG.backupSuffix;
    
    if (!fs.existsSync(targetPath)) {
        throw new Error(`目标文件不存在: ${targetPath}`);
    }
    
    fs.copyFileSync(targetPath, backupPath);
    console.log(`📁 备份文件: ${path.basename(backupPath)}`);
}

/**
 * 更新HTML文件中的题库数据
 */
function updateHtmlFile(newQuestions) {
    const targetPath = path.resolve(__dirname, CONFIG.targetFile);
    let htmlContent = fs.readFileSync(targetPath, 'utf8');
    
    // 查找EMBEDDED_QUESTIONS的开始和结束位置
    const startMarker = 'const EMBEDDED_QUESTIONS = ';
    const endMarker = '};';
    
    const startIndex = htmlContent.indexOf(startMarker);
    if (startIndex === -1) {
        throw new Error('无法找到EMBEDDED_QUESTIONS标记');
    }
    
    // 找到对应的结束位置（需要匹配大括号）
    let braceCount = 0;
    let endIndex = -1;
    let searchStart = startIndex + startMarker.length;
    
    for (let i = searchStart; i < htmlContent.length; i++) {
        if (htmlContent[i] === '{') {
            braceCount++;
        } else if (htmlContent[i] === '}') {
            braceCount--;
            if (braceCount === 0) {
                endIndex = i + 1;
                break;
            }
        }
    }
    
    if (endIndex === -1) {
        throw new Error('无法找到EMBEDDED_QUESTIONS的结束位置');
    }
    
    // 生成新的题库数据字符串
    const newQuestionsStr = JSON.stringify(newQuestions, null, 2);
    
    // 替换题库数据
    const beforeQuestions = htmlContent.substring(0, startIndex);
    const afterQuestions = htmlContent.substring(endIndex);
    
    const updatedContent = beforeQuestions + 
                          startMarker + 
                          newQuestionsStr + 
                          afterQuestions;
    
    // 写入更新后的内容
    fs.writeFileSync(targetPath, updatedContent, 'utf8');
    
    console.log(`📝 更新了 ${newQuestions.questions.length} 道题目`);
    console.log(`📈 题库版本: ${newQuestions.version}`);
    console.log(`📅 更新时间: ${newQuestions.lastUpdate}`);
}

/**
 * 验证更新结果
 */
function verifyUpdate() {
    const targetPath = path.resolve(__dirname, CONFIG.targetFile);
    const content = fs.readFileSync(targetPath, 'utf8');
    
    // 简单验证：检查是否包含EMBEDDED_QUESTIONS
    if (!content.includes('const EMBEDDED_QUESTIONS = ')) {
        throw new Error('验证失败：无法找到EMBEDDED_QUESTIONS');
    }
    
    // 检查文件大小是否合理（应该比较大，因为包含题库数据）
    const stats = fs.statSync(targetPath);
    if (stats.size < 50000) { // 50KB
        throw new Error('验证失败：文件大小异常，可能数据丢失');
    }
    
    console.log(`📊 文件大小: ${(stats.size / 1024).toFixed(1)}KB`);
}

/**
 * 显示帮助信息
 */
function showHelp() {
    console.log(`
穆桥销售测验系统 - 题库更新工具

用法:
  node update-questions.js              # 更新题库
  node update-questions.js --help       # 显示帮助

功能:
  - 从源题库文件读取最新数据
  - 自动备份现有HTML文件
  - 更新HTML文件中的内嵌题库数据
  - 验证更新结果

文件路径:
  源文件: ${CONFIG.sourceFile}
  目标文件: ${CONFIG.targetFile}

注意事项:
  - 更新前会自动创建备份文件
  - 如更新失败，可手动回滚备份文件
  - 更新后建议测试HTML文件功能
`);
}

// 处理命令行参数
const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    process.exit(0);
}

// 运行主函数
main().catch(error => {
    console.error('❌ 程序执行失败:', error);
    process.exit(1);
});