// Excel导入功能
// 需要引入SheetJS库来解析Excel文件

// 添加SheetJS库
function loadSheetJS() {
    if (window.XLSX) return Promise.resolve();
    
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Excel导入函数
async function importExcelFile(file) {
    try {
        await loadSheetJS();
        
        const data = await file.arrayBuffer();
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);
        
        console.log('Excel原始数据:', jsonData);
        
        // 转换Excel数据为标准格式
        const questions = jsonData.map((row, index) => {
            // 检测可能的列名
            const questionText = row['题目'] || row['question'] || row['题目内容'] || row['Question'] || '';
            const category = row['分类'] || row['category'] || row['Category'] || '通用';
            const type = row['类型'] || row['type'] || row['Type'] || 'single';
            
            // 选项可能的列名
            const optionA = row['选项A'] || row['A'] || row['optionA'] || row['选项1'] || '';
            const optionB = row['选项B'] || row['B'] || row['optionB'] || row['选项2'] || '';
            const optionC = row['选项C'] || row['C'] || row['optionC'] || row['选项3'] || '';
            const optionD = row['选项D'] || row['D'] || row['optionD'] || row['选项4'] || '';
            
            // 答案可能的列名
            const answer = row['答案'] || row['answer'] || row['Answer'] || row['正确答案'] || '';
            const explanation = row['解析'] || row['explanation'] || row['Explanation'] || '';
            
            return {
                category: category,
                type: type.toLowerCase() === 'multiple' || type === '多选' ? 'multiple' : 'single',
                question: questionText,
                optionA: optionA,
                optionB: optionB,
                optionC: optionC,
                optionD: optionD,
                answer: answer.toString().toUpperCase(),
                explanation: explanation
            };
        }).filter(q => q.question && q.optionA && q.optionB && q.answer);
        
        console.log('转换后的题目:', questions);
        return questions;
        
    } catch (error) {
        console.error('Excel解析错误:', error);
        throw new Error('Excel文件解析失败: ' + error.message);
    }
}