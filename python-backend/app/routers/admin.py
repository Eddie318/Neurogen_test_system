from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime, timedelta

from ..database import get_db
from ..models import SystemConfig as SystemConfigModel
from ..schemas import SystemConfigResponse, APIConfig
from ..config import settings

router = APIRouter()

@router.get("/master-config", response_model=SystemConfigResponse)
async def get_master_config(db: Session = Depends(get_db)):
    """获取系统配置（兼容现有格式）"""
    
    # 获取API配置
    api_config_record = db.query(SystemConfigModel).filter(
        SystemConfigModel.key == "api_config"
    ).first()
    
    if api_config_record and api_config_record.value:
        try:
            api_config_data = json.loads(api_config_record.value)
            # 确保配置完整
            if not api_config_data.get('key'):
                api_config_data['enabled'] = False
            else:
                api_config_data['enabled'] = True
        except:
            api_config_data = {
                "provider": "qwen",
                "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "model": "qwen-turbo",
                "key": "",
                "enabled": False
            }
    else:
        # 检查环境变量配置
        env_api_key = getattr(settings, 'qwen_api_key', '') or ''
        api_config_data = {
            "provider": "qwen", 
            "url": getattr(settings, 'qwen_api_url', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'),
            "model": getattr(settings, 'qwen_model', 'qwen-turbo'),
            "key": env_api_key,
            "enabled": bool(env_api_key)
        }
    
    return SystemConfigResponse(
        version=1,
        lastUpdate=datetime.now().isoformat(),
        apiConfig=APIConfig(**api_config_data),
        systemInfo={
            "title": "穆桥销售测验系统",
            "description": "专业销售知识测评平台",
            "examDuration": 30,
            "questionsPerExam": 15,
            "passingScore": 60
        },
        permissions={
            "allowAdminEdit": True,
            "allowApiEdit": True,
            "allowQuestionEdit": True
        }
    )

@router.put("/master-config")
async def update_master_config(
    config_data: dict,
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    try:
        # 更新API配置
        if "apiConfig" in config_data:
            api_config = config_data["apiConfig"]
            
            # 检查或创建API配置记录
            api_config_record = db.query(SystemConfigModel).filter(
                SystemConfigModel.key == "api_config"
            ).first()
            
            if api_config_record:
                api_config_record.value = json.dumps(api_config)
                api_config_record.updated_at = datetime.now()
            else:
                api_config_record = SystemConfigModel(
                    key="api_config",
                    value=json.dumps(api_config),
                    description="通义千问API配置",
                    config_type="json"
                )
                db.add(api_config_record)
        
        # 更新系统信息
        if "systemInfo" in config_data:
            system_info = config_data["systemInfo"]
            
            system_info_record = db.query(SystemConfigModel).filter(
                SystemConfigModel.key == "system_info"
            ).first()
            
            if system_info_record:
                system_info_record.value = json.dumps(system_info)
                system_info_record.updated_at = datetime.now()
            else:
                system_info_record = SystemConfigModel(
                    key="system_info",
                    value=json.dumps(system_info),
                    description="系统基础信息",
                    config_type="json"
                )
                db.add(system_info_record)
        
        db.commit()
        
        return {
            "success": True,
            "message": "配置更新成功",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"配置更新失败: {str(e)}")

@router.get("/system-status")
async def get_system_status(db: Session = Depends(get_db)):
    """获取系统状态"""
    from ..models import Question as QuestionModel, ExamRecord as ExamRecordModel
    
    # 统计数据
    total_questions = db.query(QuestionModel).count()
    total_exams = db.query(ExamRecordModel).count()
    
    # 最近7天的考试数量
    from datetime import timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_exams = db.query(ExamRecordModel).filter(
        ExamRecordModel.created_at >= seven_days_ago
    ).count()
    
    # 检查API配置状态
    api_config_record = db.query(SystemConfigModel).filter(
        SystemConfigModel.key == "api_config"
    ).first()
    
    api_configured = False
    if api_config_record and api_config_record.value:
        try:
            api_config_data = json.loads(api_config_record.value)
            api_configured = bool(api_config_data.get('key'))
        except:
            pass
    
    # 如果数据库没有配置，检查环境变量
    if not api_configured:
        api_configured = bool(getattr(settings, 'qwen_api_key', ''))
    
    return {
        "status": "healthy",
        "database": "connected",
        "api_configured": api_configured,
        "statistics": {
            "total_questions": total_questions,
            "total_exams": total_exams,
            "recent_exams": recent_exams
        },
        "server_time": datetime.now().isoformat()
    }

@router.post("/test-api")
async def test_api_connection():
    """测试API连接"""
    if not settings.qwen_api_key:
        raise HTTPException(
            status_code=400,
            detail="API密钥未配置"
        )
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.qwen_api_url,
                headers={
                    "Authorization": f"Bearer {settings.qwen_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.qwen_model,
                    "messages": [
                        {"role": "user", "content": "你好，这是一个API连接测试"}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                },
                timeout=10.0
            )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "message": "API连接测试成功",
                "response": result["choices"][0]["message"]["content"]
            }
        else:
            return {
                "success": False,
                "message": f"API调用失败: {response.status_code}",
                "error": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": "API连接测试失败",
            "error": str(e)
        }

@router.post("/api-config")
async def save_api_config(
    config_data: dict,
    db: Session = Depends(get_db)
):
    """保存API配置"""
    try:
        # 验证必要字段
        required_fields = ['provider', 'url', 'model', 'key']
        for field in required_fields:
            if field not in config_data:
                raise HTTPException(status_code=400, detail=f"缺少必要字段: {field}")
        
        # 检查或创建API配置记录
        api_config_record = db.query(SystemConfigModel).filter(
            SystemConfigModel.key == "api_config"
        ).first()
        
        if api_config_record:
            api_config_record.value = json.dumps(config_data)
            api_config_record.updated_at = datetime.now()
        else:
            api_config_record = SystemConfigModel(
                key="api_config",
                value=json.dumps(config_data),
                description="AI API配置信息",
                config_type="json"
            )
            db.add(api_config_record)
        
        db.commit()
        
        return {
            "success": True,
            "message": "API配置保存成功",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存API配置失败: {str(e)}")

@router.post("/test-api-connection")
async def test_api_connection(
    test_data: dict,
    db: Session = Depends(get_db)
):
    """测试API连接"""
    try:
        # 验证测试数据
        if 'key' not in test_data or not test_data['key']:
            return {
                "success": False,
                "message": "API密钥不能为空",
                "error": "missing_api_key"
            }
        
        provider = test_data.get('provider', 'qwen')
        url = test_data.get('url', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')
        model = test_data.get('model', 'qwen-turbo')
        api_key = test_data['key']
        
        import httpx
        
        # 判断是否使用OpenAI兼容格式
        is_openai_compatible = 'compatible-mode' in url or 'chat/completions' in url or provider != 'qwen'
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if is_openai_compatible:
            # OpenAI兼容格式
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "你好，这是一个API连接测试"}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
        else:
            # 原生Qwen格式
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {"role": "user", "content": "你好，这是一个API连接测试"}
                    ]
                },
                "parameters": {
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=15.0
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # 解析响应内容
            if is_openai_compatible:
                if 'choices' in result and len(result['choices']) > 0:
                    response_text = result['choices'][0]['message']['content']
                else:
                    response_text = "API响应格式正确"
            else:
                if 'output' in result and 'text' in result['output']:
                    response_text = result['output']['text']
                else:
                    response_text = "API响应格式正确"
                    
            return {
                "success": True,
                "message": "API连接测试成功",
                "response": response_text[:100]  # 限制响应长度
            }
        else:
            return {
                "success": False,
                "message": f"API调用失败: HTTP {response.status_code}",
                "error": response.text[:200]  # 限制错误信息长度
            }
            
    except httpx.TimeoutException:
        return {
            "success": False,
            "message": "API连接超时",
            "error": "connection_timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "message": "API连接测试失败",
            "error": str(e)[:200]  # 限制错误信息长度
        }

@router.get("/config/{key}")
async def get_config(key: str, db: Session = Depends(get_db)):
    """获取单个配置项"""
    config = db.query(SystemConfigModel).filter(
        SystemConfigModel.key == key
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置项不存在")
    
    return {
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "updated_at": config.updated_at
    }

@router.put("/config/{key}")
async def update_config(
    key: str,
    config_data: dict,
    db: Session = Depends(get_db)
):
    """更新单个配置项"""
    config = db.query(SystemConfigModel).filter(
        SystemConfigModel.key == key
    ).first()
    
    if config:
        config.value = json.dumps(config_data.get("value"))
        config.description = config_data.get("description", config.description)
        config.updated_at = datetime.now()
    else:
        config = SystemConfigModel(
            key=key,
            value=json.dumps(config_data.get("value")),
            description=config_data.get("description", ""),
            config_type=config_data.get("type", "string")
        )
        db.add(config)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"配置项 {key} 更新成功"
    }

@router.get("/questions/stats")
async def get_questions_stats(db: Session = Depends(get_db)):
    """获取题库统计信息"""
    from ..models import Question as QuestionModel
    from sqlalchemy import func
    
    # 总题目数
    total_questions = db.query(QuestionModel).count()
    
    # 按类型统计
    type_stats = db.query(
        QuestionModel.question_type,
        func.count(QuestionModel.id).label('count')
    ).group_by(QuestionModel.question_type).all()
    
    # 按分类统计
    category_stats = db.query(
        QuestionModel.category,
        func.count(QuestionModel.id).label('count')
    ).group_by(QuestionModel.category).all()
    
    # 转换统计结果
    type_breakdown = {}
    for stat in type_stats:
        type_name = "单选题" if stat.question_type == "single" else "多选题" if stat.question_type == "multiple" else stat.question_type
        type_breakdown[type_name] = stat.count
    
    category_breakdown = {}
    for stat in category_stats:
        category_breakdown[stat.category] = stat.count
    
    return {
        "total_questions": total_questions,
        "type_breakdown": type_breakdown,
        "category_breakdown": category_breakdown,
        "statistics": {
            "single_choice": type_breakdown.get("单选题", 0),
            "multiple_choice": type_breakdown.get("多选题", 0),
            "categories": len(category_breakdown),
            "last_updated": datetime.now().isoformat()
        }
    }

@router.get("/questions/export")
async def export_questions_json(db: Session = Depends(get_db)):
    """导出题库为JSON格式"""
    from ..models import Question as QuestionModel
    
    questions = db.query(QuestionModel).all()
    
    # 转换为导出格式
    export_data = {
        "version": 2,
        "export_time": datetime.now().isoformat(),
        "total_questions": len(questions),
        "questions": []
    }
    
    for q in questions:
        question_data = {
            "id": q.id,
            "questionId": q.question_id or q.id,
            "category": q.category,
            "type": q.question_type,
            "question": q.question,
            "optionA": q.option_a,
            "optionB": q.option_b,
            "optionC": q.option_c,
            "optionD": q.option_d,
            "answer": q.answer,
            "explanation": q.explanation or "",
            "created_at": q.created_at.isoformat() if q.created_at else None
        }
        export_data["questions"].append(question_data)
    
    return export_data

@router.post("/daily-exam-config")
async def save_daily_exam_config(
    config_data: dict,
    db: Session = Depends(get_db)
):
    """保存每日考试配置"""
    try:
        # 验证必要字段
        required_fields = ['daily_exam_start_time', 'daily_exam_end_time', 'daily_exam_question_count', 'daily_exam_duration_minutes']
        for field in required_fields:
            if field not in config_data:
                raise HTTPException(status_code=400, detail=f"缺少必要字段: {field}")
        
        # 检查或创建每日考试配置记录
        daily_config_record = db.query(SystemConfigModel).filter(
            SystemConfigModel.key == "daily_exam_config"
        ).first()
        
        if daily_config_record:
            daily_config_record.value = json.dumps(config_data)
            daily_config_record.updated_at = datetime.now()
        else:
            daily_config_record = SystemConfigModel(
                key="daily_exam_config",
                value=json.dumps(config_data),
                description="每日考试时间配置",
                config_type="json"
            )
            db.add(daily_config_record)
        
        db.commit()
        
        return {
            "success": True,
            "message": "每日考试配置保存成功",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"保存每日考试配置失败: {str(e)}")

@router.get("/daily-exam-config")
async def get_daily_exam_config(db: Session = Depends(get_db)):
    """获取每日考试配置"""
    daily_config_record = db.query(SystemConfigModel).filter(
        SystemConfigModel.key == "daily_exam_config"
    ).first()
    
    if daily_config_record and daily_config_record.value:
        try:
            config_data = json.loads(daily_config_record.value)
            return {
                "success": True,
                "config": config_data,
                "updated_at": daily_config_record.updated_at.isoformat() if daily_config_record.updated_at else None
            }
        except:
            pass
    
    # 返回默认配置
    return {
        "success": True,
        "config": {
            "daily_exam_start_time": "08:00",
            "daily_exam_end_time": "20:00", 
            "daily_exam_question_count": 3,
            "daily_exam_duration_minutes": 10
        },
        "updated_at": None
    }

@router.get("/daily-exam-report")
async def get_daily_exam_report(
    date: str = None,
    db: Session = Depends(get_db)
):
    """获取每日考试报告"""
    from ..models import ExamRecord as ExamRecordModel
    from sqlalchemy import func, and_
    
    # 如果没有指定日期，使用今天
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 解析日期
        target_date = datetime.strptime(date, '%Y-%m-%d')
        next_date = target_date + timedelta(days=1)
        
        # 查询当日每日测验记录
        daily_records = db.query(ExamRecordModel).filter(
            and_(
                ExamRecordModel.exam_type == 'daily_exam',
                ExamRecordModel.created_at >= target_date,
                ExamRecordModel.created_at < next_date
            )
        ).all()
        
        if not daily_records:
            return {
                "date": date,
                "has_data": False,
                "message": "当日无考试记录"
            }
        
        # 统计数据
        total_participants = len(daily_records)
        total_score = sum(record.score for record in daily_records)
        average_score = round(total_score / total_participants, 2)
        
        # 分数段统计
        excellent_count = len([r for r in daily_records if r.score >= 90])
        good_count = len([r for r in daily_records if 70 <= r.score < 90])
        average_count = len([r for r in daily_records if 60 <= r.score < 70])
        poor_count = len([r for r in daily_records if r.score < 60])
        
        # 计算平均用时
        total_duration = sum(record.duration for record in daily_records if record.duration)
        avg_duration = round(total_duration / total_participants) if total_duration > 0 else 0
        
        return {
            "date": date,
            "has_data": True,
            "statistics": {
                "total_participants": total_participants,
                "average_score": average_score,
                "average_duration_seconds": avg_duration,
                "score_distribution": {
                    "excellent": {"count": excellent_count, "percentage": round(excellent_count/total_participants*100, 1)},
                    "good": {"count": good_count, "percentage": round(good_count/total_participants*100, 1)},
                    "average": {"count": average_count, "percentage": round(average_count/total_participants*100, 1)},
                    "poor": {"count": poor_count, "percentage": round(poor_count/total_participants*100, 1)}
                }
            },
            "records": [
                {
                    "user_name": record.user_name,
                    "score": record.score,
                    "correct_count": record.correct_count,
                    "total_questions": record.total_questions,
                    "duration": record.duration,
                    "created_at": record.created_at.isoformat()
                }
                for record in daily_records
            ]
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成每日报告失败: {str(e)}")

@router.post("/generate-daily-reports")
async def generate_daily_reports(db: Session = Depends(get_db)):
    """生成所有缺失的每日报告"""
    from ..models import ExamRecord as ExamRecordModel
    from sqlalchemy import func, distinct
    
    try:
        # 获取所有有每日测验记录的日期
        exam_dates = db.query(
            func.date(ExamRecordModel.created_at).label('exam_date')
        ).filter(
            ExamRecordModel.exam_type == 'daily_exam'
        ).distinct().all()
        
        generated_reports = []
        
        for date_tuple in exam_dates:
            exam_date = date_tuple[0]
            date_str = exam_date.strftime('%Y-%m-%d')
            
            # 检查是否已有报告记录
            existing_report = db.query(SystemConfigModel).filter(
                SystemConfigModel.key == f"daily_report_{date_str}"
            ).first()
            
            if not existing_report:
                # 生成该日期的报告
                report_data = await get_daily_exam_report(date_str, db)
                
                if report_data["has_data"]:
                    # 保存报告到数据库
                    report_record = SystemConfigModel(
                        key=f"daily_report_{date_str}",
                        value=json.dumps(report_data),
                        description=f"{date_str}每日考试报告",
                        config_type="json"
                    )
                    db.add(report_record)
                    generated_reports.append(date_str)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"成功生成 {len(generated_reports)} 个每日报告",
            "generated_dates": generated_reports
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成每日报告失败: {str(e)}")