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
            
            return {
                "success": True,
                "message": "考试记录更新成功",
                "id": existing.id,
                "action": "updated"
            }
        else:
            # 创建新记录
            db_record = ExamRecordModel(**exam_record.dict())
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            
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
        
        # 准备AI分析数据
        exam_data = request.exam_data
        prompt = f"""
请基于以下考试数据生成一份专业的医药代表知识掌握分析报告：

考试信息：
- 姓名：{exam_record.user_name}
- 分数：{exam_record.score}分（满分100分）
- 正确率：{exam_record.correct_count}/{exam_record.total_questions} = {round(exam_record.correct_count/exam_record.total_questions*100, 1)}%
- 考试用时：{exam_record.duration // 60}分{exam_record.duration % 60}秒

答题详情：
{json.dumps(exam_data, ensure_ascii=False, indent=2)}

请从以下几个方面进行分析：
1. 整体表现评估
2. 知识结构强弱分析
3. 错题原因分析
4. 改进建议
5. 学习重点推荐

请用专业、客观的语言，为医药代表提供有价值的学习指导。
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