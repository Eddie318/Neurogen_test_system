from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import httpx
from datetime import datetime, timedelta

from ..database import get_db
from ..models import ExamRecord as ExamRecordModel, SystemConfig as SystemConfigModel
from ..schemas import ExamRecord, ExamRecordCreate, AIReportRequest, AIReportResponse
from ..config import settings

router = APIRouter()

async def _generate_auto_report(exam_record: ExamRecordModel, db: Session):
    """自动生成AI报告的内部函数"""
    try:
        # 获取API配置
        api_config_record = db.query(SystemConfigModel).filter(
            SystemConfigModel.key == "api_config"
        ).first()
        
        api_config = None
        if api_config_record and api_config_record.value:
            try:
                api_config = json.loads(api_config_record.value)
            except:
                pass
        
        # 如果数据库没有配置，使用环境变量
        if not api_config or not api_config.get('key'):
            env_api_key = getattr(settings, 'qwen_api_key', '')
            if not env_api_key:
                return  # 没有API密钥就跳过
                
            api_config = {
                "provider": "qwen",
                "url": getattr(settings, 'qwen_api_url', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'),
                "model": getattr(settings, 'qwen_model', 'qwen-turbo'),
                "key": env_api_key
            }
        
        # 获取题目信息进行专业解析
        # 优先使用传递的题目数据，如果没有则使用旧方法
        question_analysis = []
        
        # 检查是否有完整的题目数据
        if hasattr(exam_record, 'questions_data') and exam_record.questions_data:
            # 使用前端传递的完整题目数据
            try:
                questions_data = exam_record.questions_data
                if isinstance(questions_data, str):
                    questions_data = json.loads(questions_data)
                
                for i, q_data in enumerate(questions_data):
                    question_analysis.append({
                        "question": q_data.get("question", ""),
                        "category": q_data.get("category", ""),
                        "type": q_data.get("question_type", "single"),
                        "correct_answer": q_data.get("correct_answer", ""),
                        "user_answer": q_data.get("user_answer", ""),
                        "is_correct": q_data.get("is_correct", False),
                        "explanation": q_data.get("explanation", "")
                    })
            except Exception as e:
                print(f"解析题目数据失败: {e}")
                # 如果解析失败，使用旧方法
                question_analysis = []
        
        # 如果没有题目数据，使用旧方法（保持兼容性）
        if not question_analysis:
            from ..models import Question as QuestionModel
            detailed_answers = json.loads(exam_record.detailed_answers) if isinstance(exam_record.detailed_answers, str) else exam_record.detailed_answers
            
            if detailed_answers:
                question_ids = list(detailed_answers.keys())
                questions = db.query(QuestionModel).limit(len(question_ids)).all()
                
                for i, (q_key, user_answer) in enumerate(detailed_answers.items()):
                    if i < len(questions):
                        q = questions[i]
                        is_correct = user_answer.upper().strip() == q.answer.upper().strip()
                        question_analysis.append({
                            "question": q.question,
                            "category": q.category,
                            "type": q.question_type,
                            "correct_answer": q.answer,
                            "user_answer": user_answer,
                            "is_correct": is_correct,
                            "explanation": q.explanation or ""
                        })
        
        # 准备AI分析数据
        prompt = f"""
基于以下测验结果，请为医药代表生成一份简洁的专业评价报告：

**测验信息：**
- 姓名：{exam_record.user_name}
- 得分：{exam_record.score}分（满分100分）
- 正确率：{exam_record.correct_count}/{exam_record.total_questions} = {round(exam_record.correct_count/exam_record.total_questions*100, 1)}%
- 用时：{exam_record.duration // 60}分{exam_record.duration % 60}秒

**题目解析：**
{json.dumps(question_analysis, ensure_ascii=False, indent=2)}

请提供：
1. **简要表现评价**（2-3句话）
2. **错题专业解析**（针对每道错题，简述知识点和正确理解）
3. **改进建议**（2-3条具体建议）
4. **学习重点**（推荐重点学习的知识模块）

要求：
- 内容简洁实用，总字数控制在500字以内
- 专业术语准确，重点突出实用性
- 针对医药代表工作需要提供指导
        """
        
        # 调用AI API
        provider = api_config.get('provider', 'qwen')
        url = api_config['url']
        
        # 判断是否使用OpenAI兼容格式
        is_openai_compatible = 'compatible-mode' in url or 'chat/completions' in url or provider != 'qwen'
        
        headers = {
            "Authorization": f"Bearer {api_config['key']}",
            "Content-Type": "application/json"
        }
        
        if is_openai_compatible:
            # OpenAI兼容格式
            payload = {
                "model": api_config['model'],
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,  # 减少token限制以保持简洁
                "temperature": 0.3   # 降低温度以提高准确性
            }
        else:
            # 原生Qwen格式
            payload = {
                "model": api_config['model'],
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "max_tokens": 1000,
                    "temperature": 0.3
                }
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # 根据不同格式解析响应
            if is_openai_compatible:
                # OpenAI兼容格式
                if 'choices' in result and len(result['choices']) > 0:
                    ai_report = result['choices'][0]['message']['content']
                else:
                    return  # 解析失败就跳过
            else:
                # 原生Qwen格式
                if 'output' in result and 'text' in result['output']:
                    ai_report = result['output']['text']
                else:
                    return  # 解析失败就跳过
            
            # 保存AI报告到数据库
            exam_record.ai_report = ai_report
            db.commit()
            
    except Exception as e:
        # 自动生成失败不影响主流程，只记录错误但不抛出异常
        print(f"自动生成AI报告失败: {str(e)}")
        pass

async def _generate_auto_report_async(record_id: str, old_db: Session):
    """异步生成AI报告，不阻塞主请求"""
    try:
        # 创建新的数据库会话
        from ..database import SessionLocal
        db = SessionLocal()
        
        try:
            # 重新获取记录
            exam_record = db.query(ExamRecordModel).filter(
                ExamRecordModel.id == record_id
            ).first()
            
            if not exam_record or exam_record.ai_report:
                return  # 记录不存在或已有报告就跳过
                
            # 调用原有的生成逻辑
            await _generate_auto_report(exam_record, db)
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"异步生成AI报告失败: {str(e)}")
        pass

@router.get("/exam-records", response_model=List[ExamRecord])
async def get_exam_records(
    user_name: Optional[str] = None,
    department: Optional[str] = None,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db)
):
    """获取考试记录列表"""
    query = db.query(ExamRecordModel)
    
    if user_name:
        query = query.filter(ExamRecordModel.user_name.contains(user_name))
    
    if department:
        query = query.filter(ExamRecordModel.department == department)
    
    # 按创建时间倒序
    query = query.order_by(ExamRecordModel.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

@router.post("/exam-records", response_model=dict)
async def save_exam_record(
    exam_record: ExamRecordCreate,
    db: Session = Depends(get_db)
):
    """保存考试记录"""
    try:
        # 检查记录是否已存在
        existing = db.query(ExamRecordModel).filter(
            ExamRecordModel.id == exam_record.id
        ).first()
        
        if existing:
            # 更新现有记录
            for key, value in exam_record.dict(exclude_unset=True).items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            
            # 如果没有AI报告，异步生成（不阻塞响应）
            if not existing.ai_report:
                import asyncio
                asyncio.create_task(_generate_auto_report_async(existing.id, db))
            
            return {
                "success": True,
                "message": "考试记录更新成功",
                "id": existing.id,
                "action": "updated"
            }
        else:
            # 创建新记录时，自动填充当前团队和题库信息
            from ..models import SystemConfig
            
            record_data = exam_record.dict()
            
            # 如果没有指定team_id和bank_id，使用当前配置
            if 'team_id' not in record_data or record_data['team_id'] is None:
                team_config = db.query(SystemConfig).filter(SystemConfig.key == "current_team_id").first()
                record_data['team_id'] = int(team_config.value) if team_config else 1
            
            if 'bank_id' not in record_data or record_data['bank_id'] is None:
                bank_config = db.query(SystemConfig).filter(SystemConfig.key == "current_bank_id").first()
                record_data['bank_id'] = int(bank_config.value) if bank_config else 1
            
            db_record = ExamRecordModel(**record_data)
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            
            # 异步生成AI报告（不阻塞响应）
            import asyncio
            asyncio.create_task(_generate_auto_report_async(db_record.id, db))
            
            return {
                "success": True,
                "message": "考试记录保存成功",
                "id": db_record.id,
                "action": "created"
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存失败: {str(e)}")

@router.get("/exam-records/{record_id}", response_model=ExamRecord)
async def get_exam_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """获取单个考试记录详情"""
    record = db.query(ExamRecordModel).filter(
        ExamRecordModel.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    
    return record

@router.delete("/exam-records/{record_id}")
async def delete_exam_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """删除考试记录"""
    record = db.query(ExamRecordModel).filter(
        ExamRecordModel.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    
    db.delete(record)
    db.commit()
    
    return {"message": "考试记录删除成功"}

@router.post("/generate-ai-report", response_model=AIReportResponse)
async def generate_ai_report(
    request: AIReportRequest,
    db: Session = Depends(get_db)
):
    """生成AI分析报告"""
    try:
        # 获取考试记录
        exam_record = db.query(ExamRecordModel).filter(
            ExamRecordModel.id == request.exam_record_id
        ).first()
        
        if not exam_record:
            raise HTTPException(status_code=404, detail="考试记录不存在")
        
        # 获取API配置
        api_config_record = db.query(SystemConfigModel).filter(
            SystemConfigModel.key == "api_config"
        ).first()
        
        api_config = None
        if api_config_record and api_config_record.value:
            try:
                api_config = json.loads(api_config_record.value)
            except:
                pass
        
        # 如果数据库没有配置，使用环境变量
        if not api_config or not api_config.get('key'):
            env_api_key = getattr(settings, 'qwen_api_key', '')
            if not env_api_key:
                raise HTTPException(
                    status_code=400, 
                    detail="未配置API密钥，请先在系统配置中设置"
                )
            api_config = {
                "provider": "qwen",
                "url": getattr(settings, 'qwen_api_url', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'),
                "model": getattr(settings, 'qwen_model', 'qwen-turbo'),
                "key": env_api_key
            }
        
        # 获取具体题目信息进行专业解析
        from ..models import Question as QuestionModel
        detailed_answers = json.loads(exam_record.detailed_answers) if isinstance(exam_record.detailed_answers, str) else exam_record.detailed_answers
        
        # 获取题目信息
        question_analysis = []
        if detailed_answers:
            question_ids = list(detailed_answers.keys())
            # 简化版本：假设题目ID对应数据库中的顺序
            questions = db.query(QuestionModel).limit(len(question_ids)).all()
            
            for i, (q_key, user_answer) in enumerate(detailed_answers.items()):
                if i < len(questions):
                    q = questions[i]
                    is_correct = user_answer.upper().strip() == q.answer.upper().strip()
                    question_analysis.append({
                        "question": q.question,
                        "category": q.category,
                        "type": q.question_type,
                        "correct_answer": q.answer,
                        "user_answer": user_answer,
                        "is_correct": is_correct,
                        "explanation": q.explanation or ""
                    })
        
        # 准备AI分析数据
        exam_data = request.exam_data
        prompt = f"""
基于以下测验结果，请为医药代表生成一份简洁的专业评价报告：

**测验信息：**
- 姓名：{exam_record.user_name}
- 得分：{exam_record.score}分（满分100分）
- 正确率：{exam_record.correct_count}/{exam_record.total_questions} = {round(exam_record.correct_count/exam_record.total_questions*100, 1)}%
- 用时：{exam_record.duration // 60}分{exam_record.duration % 60}秒

**题目解析：**
{json.dumps(question_analysis, ensure_ascii=False, indent=2)}

请提供：
1. **简要表现评价**（2-3句话）
2. **错题专业解析**（针对每道错题，简述知识点和正确理解）
3. **改进建议**（2-3条具体建议）
4. **学习重点**（推荐重点学习的知识模块）

要求：
- 内容简洁实用，总字数控制在500字以内
- 专业术语准确，重点突出实用性
- 针对医药代表工作需要提供指导
        """
        
        # 调用AI API
        provider = api_config.get('provider', 'qwen')
        url = api_config['url']
        
        # 判断是否使用OpenAI兼容格式
        is_openai_compatible = 'compatible-mode' in url or 'chat/completions' in url or provider != 'qwen'
        
        headers = {
            "Authorization": f"Bearer {api_config['key']}",
            "Content-Type": "application/json"
        }
        
        if is_openai_compatible:
            # OpenAI兼容格式
            payload = {
                "model": api_config['model'],
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
        else:
            # 原生Qwen格式
            payload = {
                "model": api_config['model'],
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # 根据不同格式解析响应
            if is_openai_compatible:
                # OpenAI兼容格式
                if 'choices' in result and len(result['choices']) > 0:
                    ai_report = result['choices'][0]['message']['content']
                else:
                    raise ValueError("OpenAI兼容API响应格式异常")
            else:
                # 原生Qwen格式
                if 'output' in result and 'text' in result['output']:
                    ai_report = result['output']['text']
                else:
                    raise ValueError("通义千问API响应格式异常")
            
            # 保存AI报告到数据库
            exam_record.ai_report = ai_report
            db.commit()
            
            return AIReportResponse(
                success=True,
                report=ai_report
            )
        else:
            error_detail = f"API调用失败: {response.status_code} - {response.text}"
            return AIReportResponse(
                success=False,
                error=error_detail
            )
            
    except httpx.TimeoutException:
        return AIReportResponse(
            success=False,
            error="API调用超时，请稍后重试"
        )
    except Exception as e:
        return AIReportResponse(
            success=False,
            error=f"生成报告失败: {str(e)}"
        )

@router.get("/exam-analytics")
async def get_exam_analytics(
    days: int = 30,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取考试数据分析"""
    # 计算时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 基础查询
    query = db.query(ExamRecordModel).filter(
        ExamRecordModel.created_at >= start_date,
        ExamRecordModel.created_at <= end_date
    )
    
    if department:
        query = query.filter(ExamRecordModel.department == department)
    
    records = query.all()
    
    if not records:
        return {
            "total_exams": 0,
            "avg_score": 0,
            "high_performers": 0,
            "low_performers": 0,
            "department_stats": [],
            "daily_stats": []
        }
    
    # 基础统计
    total_exams = len(records)
    avg_score = sum(r.score for r in records) / total_exams
    high_performers = len([r for r in records if r.score >= 80])
    low_performers = len([r for r in records if r.score < 60])
    
    # 部门统计
    dept_stats = {}
    for record in records:
        dept = record.department or "未分组"
        if dept not in dept_stats:
            dept_stats[dept] = []
        dept_stats[dept].append(record.score)
    
    department_stats = []
    for dept, scores in dept_stats.items():
        department_stats.append({
            "department": dept,
            "exam_count": len(scores),
            "avg_score": sum(scores) / len(scores),
            "high_performers": len([s for s in scores if s >= 80]),
            "low_performers": len([s for s in scores if s < 60])
        })
    
    # 按日期统计
    daily_stats = {}
    for record in records:
        date_key = record.created_at.strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = []
        daily_stats[date_key].append(record.score)
    
    daily_list = []
    for date, scores in sorted(daily_stats.items()):
        daily_list.append({
            "date": date,
            "exam_count": len(scores),
            "avg_score": sum(scores) / len(scores)
        })
    
    return {
        "total_exams": total_exams,
        "avg_score": round(avg_score, 1),
        "high_performers": high_performers,
        "low_performers": low_performers,
        "department_stats": department_stats,
        "daily_stats": daily_list,
        "analysis_period": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
    }