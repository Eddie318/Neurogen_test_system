"""
考试管理路由 - 创建、管理正式考试
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Exam as ExamModel, ExamQuestion as ExamQuestionModel, Question as QuestionModel
from ..schemas import (
    ExamCreate, ExamUpdate, Exam, ExamWithQuestions, ExamList,
    Question, QuestionBank
)

router = APIRouter()

@router.get("/exams", response_model=List[ExamList])
async def get_exams(
    exam_type: Optional[str] = Query(None, description="考试类型：formal或practice"),
    status: Optional[str] = Query(None, description="考试状态：upcoming, active, expired"),
    db: Session = Depends(get_db)
):
    """获取考试列表"""
    query = db.query(ExamModel)
    
    # 过滤考试类型
    if exam_type:
        query = query.filter(ExamModel.exam_type == exam_type)
    
    exams = query.order_by(ExamModel.created_at.desc()).all()
    
    # 构建返回数据
    result = []
    now = datetime.now()
    
    for exam in exams:
        # 统计考试题目数量
        question_count = db.query(ExamQuestionModel).filter(
            ExamQuestionModel.exam_id == exam.id
        ).count()
        
        # 判断考试状态
        if now < exam.start_time:
            exam_status = "upcoming"
        elif now > exam.end_time:
            exam_status = "expired"
        else:
            exam_status = "active"
        
        # 如果指定了状态过滤
        if status and exam_status != status:
            continue
            
        exam_data = ExamList(
            id=exam.id,
            exam_name=exam.exam_name,
            description=exam.description,
            exam_type=exam.exam_type,
            duration_minutes=exam.duration_minutes,
            start_time=exam.start_time,
            end_time=exam.end_time,
            is_active=exam.is_active,
            total_questions=question_count,
            status=exam_status
        )
        result.append(exam_data)
    
    return result

@router.get("/exams/{exam_id}", response_model=ExamWithQuestions)
async def get_exam_detail(exam_id: int, db: Session = Depends(get_db)):
    """获取考试详情（包含题目）"""
    exam = db.query(ExamModel).filter(ExamModel.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    # 获取考试题目
    exam_questions = db.query(ExamQuestionModel).options(
        joinedload(ExamQuestionModel.question)
    ).filter(
        ExamQuestionModel.exam_id == exam_id
    ).order_by(ExamQuestionModel.order_index).all()
    
    questions = []
    for eq in exam_questions:
        q = eq.question
        question_dict = Question(
            id=q.id,
            category=q.category,
            question_type=q.question_type,
            question=q.question,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            answer=q.answer,
            explanation=q.explanation,
            question_id=q.question_id,
            created_at=q.created_at,
            updated_at=q.updated_at
        )
        questions.append(question_dict)
    
    return ExamWithQuestions(
        id=exam.id,
        exam_name=exam.exam_name,
        description=exam.description,
        exam_type=exam.exam_type,
        duration_minutes=exam.duration_minutes,
        start_time=exam.start_time,
        end_time=exam.end_time,
        is_active=exam.is_active,
        created_by=exam.created_by,
        created_at=exam.created_at,
        updated_at=exam.updated_at,
        questions=questions,
        total_questions=len(questions)
    )

@router.get("/exams/{exam_id}/questions", response_model=QuestionBank)
async def get_exam_questions(
    exam_id: int, 
    sales: Optional[bool] = Query(False, description="销售模式，移除答案"),
    db: Session = Depends(get_db)
):
    """获取考试题目（适配前端考试页面格式）"""
    exam = db.query(ExamModel).filter(ExamModel.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    # 检查考试时间
    now = datetime.now()
    if now < exam.start_time:
        raise HTTPException(status_code=400, detail="考试尚未开始")
    if now > exam.end_time:
        raise HTTPException(status_code=400, detail="考试已结束")
    if not exam.is_active:
        raise HTTPException(status_code=400, detail="考试已关闭")
    
    # 获取考试题目
    exam_questions = db.query(ExamQuestionModel).options(
        joinedload(ExamQuestionModel.question)
    ).filter(
        ExamQuestionModel.exam_id == exam_id
    ).order_by(ExamQuestionModel.order_index).all()
    
    question_data = []
    for eq in exam_questions:
        q = eq.question
        question_dict = {
            "id": q.id,
            "category": q.category,
            "type": q.question_type,
            "question": q.question,
            "optionA": q.option_a,
            "optionB": q.option_b,
            "optionC": q.option_c,
            "optionD": q.option_d,
            "questionId": q.question_id or q.id
        }
        
        # 销售模式下移除答案和解析
        if not sales:
            question_dict["answer"] = q.answer
            question_dict["explanation"] = q.explanation or ""
        
        question_data.append(question_dict)
    
    return QuestionBank(
        version=1,
        lastUpdate=exam.updated_at.isoformat(),
        totalQuestions=len(question_data),
        categories=list(set([q.category for q in [eq.question for eq in exam_questions]])),
        maintainer="管理员",
        questions=question_data,
        exam_id=exam_id,
        exam_name=exam.exam_name,
        duration_minutes=exam.duration_minutes
    )

@router.post("/exams", response_model=Exam)
async def create_exam(exam_data: ExamCreate, db: Session = Depends(get_db)):
    """创建新考试"""
    
    # 验证题目是否存在
    questions = db.query(QuestionModel).filter(
        QuestionModel.id.in_(exam_data.question_ids)
    ).all()
    
    if len(questions) != len(exam_data.question_ids):
        raise HTTPException(status_code=400, detail="部分题目不存在")
    
    # 创建考试
    exam = ExamModel(
        exam_name=exam_data.exam_name,
        description=exam_data.description,
        exam_type=exam_data.exam_type,
        duration_minutes=exam_data.duration_minutes,
        start_time=exam_data.start_time,
        end_time=exam_data.end_time,
        is_active=exam_data.is_active
    )
    
    db.add(exam)
    db.commit()
    db.refresh(exam)
    
    # 添加考试题目关联
    for index, question_id in enumerate(exam_data.question_ids):
        exam_question = ExamQuestionModel(
            exam_id=exam.id,
            question_id=question_id,
            order_index=index + 1
        )
        db.add(exam_question)
    
    db.commit()
    
    return exam

@router.put("/exams/{exam_id}", response_model=Exam)
async def update_exam(
    exam_id: int, 
    exam_data: ExamUpdate, 
    db: Session = Depends(get_db)
):
    """更新考试"""
    exam = db.query(ExamModel).filter(ExamModel.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    # 更新考试基本信息
    update_data = exam_data.dict(exclude_unset=True, exclude={"question_ids"})
    for field, value in update_data.items():
        setattr(exam, field, value)
    
    # 更新题目关联
    if exam_data.question_ids is not None:
        # 删除原有关联
        db.query(ExamQuestionModel).filter(
            ExamQuestionModel.exam_id == exam_id
        ).delete()
        
        # 验证题目存在
        questions = db.query(QuestionModel).filter(
            QuestionModel.id.in_(exam_data.question_ids)
        ).all()
        
        if len(questions) != len(exam_data.question_ids):
            raise HTTPException(status_code=400, detail="部分题目不存在")
        
        # 添加新关联
        for index, question_id in enumerate(exam_data.question_ids):
            exam_question = ExamQuestionModel(
                exam_id=exam_id,
                question_id=question_id,
                order_index=index + 1
            )
            db.add(exam_question)
    
    db.commit()
    db.refresh(exam)
    
    return exam

@router.delete("/exams/{exam_id}")
async def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    """删除考试"""
    exam = db.query(ExamModel).filter(ExamModel.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    # 删除考试题目关联
    db.query(ExamQuestionModel).filter(
        ExamQuestionModel.exam_id == exam_id
    ).delete()
    
    # 删除考试
    db.delete(exam)
    db.commit()
    
    return {"message": "考试删除成功"}

@router.post("/exams/{exam_id}/toggle")
async def toggle_exam_status(exam_id: int, db: Session = Depends(get_db)):
    """切换考试状态（启用/禁用）"""
    exam = db.query(ExamModel).filter(ExamModel.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    exam.is_active = not exam.is_active
    db.commit()
    
    return {"message": f"考试已{'启用' if exam.is_active else '禁用'}", "is_active": exam.is_active}