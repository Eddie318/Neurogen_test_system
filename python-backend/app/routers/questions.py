from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import random
from datetime import datetime

from ..database import get_db
from ..models import Question as QuestionModel
from ..schemas import Question, QuestionCreate, QuestionBank, QuestionBase

router = APIRouter()

@router.get("/questions", response_model=List[Question])
async def get_questions(
    category: Optional[str] = Query(None, description="题目分类筛选"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),
    limit: Optional[int] = Query(None, description="返回数量限制"),
    random_sample: bool = Query(False, description="是否随机抽取"),
    db: Session = Depends(get_db)
):
    """获取题库列表"""
    query = db.query(QuestionModel)
    
    if category:
        query = query.filter(QuestionModel.category == category)
    
    if question_type:
        query = query.filter(QuestionModel.question_type == question_type)
    
    questions = query.all()
    
    if random_sample and limit:
        questions = random.sample(questions, min(limit, len(questions)))
    elif limit:
        questions = questions[:limit]
    
    return questions

@router.get("/master-questions", response_model=QuestionBank)
async def get_master_questions(
    sales: Optional[bool] = Query(False, description="销售模式，移除答案"),
    db: Session = Depends(get_db)
):
    """获取完整题库数据（兼容现有格式）"""
    questions = db.query(QuestionModel).all()
    
    # 获取分类列表
    categories = list(set([q.category for q in questions]))
    
    # 转换为兼容格式
    question_data = []
    for q in questions:
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
        version=2,
        lastUpdate=datetime.now().isoformat(),
        totalQuestions=len(questions),
        categories=categories,
        maintainer="管理员",
        questions=question_data
    )

@router.post("/questions", response_model=Question)
async def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db)
):
    """创建新题目"""
    db_question = QuestionModel(
        category=question.category,
        question_type=question.question_type,
        question=question.question,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        answer=question.answer,
        explanation=question.explanation,
        question_id=question.question_id
    )
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return db_question

@router.put("/questions/{question_id}", response_model=Question)
async def update_question(
    question_id: int,
    question_update: dict,
    db: Session = Depends(get_db)
):
    """更新题目"""
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    
    if not db_question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 更新字段
    for key, value in question_update.items():
        if hasattr(db_question, key) and value is not None:
            setattr(db_question, key, value)
    
    db.commit()
    db.refresh(db_question)
    
    return db_question

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """删除题目"""
    db_question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
    
    if not db_question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    db.delete(db_question)
    db.commit()
    
    return {"message": "题目删除成功"}

@router.post("/questions/import")
async def import_questions_from_json(
    questions_data: dict,
    db: Session = Depends(get_db)
):
    """从JSON数据导入题库"""
    try:
        questions = questions_data.get("questions", [])
        imported_count = 0
        
        for q_data in questions:
            # 检查是否已存在相同题目
            existing = db.query(QuestionModel).filter(
                QuestionModel.question == q_data["question"]
            ).first()
            
            if existing:
                continue
            
            db_question = QuestionModel(
                category=q_data["category"],
                question_type=q_data["type"],
                question=q_data["question"],
                option_a=q_data["optionA"],
                option_b=q_data["optionB"],
                option_c=q_data.get("optionC"),
                option_d=q_data.get("optionD"),
                answer=q_data["answer"],
                explanation=q_data.get("explanation", ""),
                question_id=q_data.get("questionId")
            )
            
            db.add(db_question)
            imported_count += 1
        
        db.commit()
        
        return {
            "message": f"成功导入 {imported_count} 道题目",
            "imported_count": imported_count,
            "total_questions": db.query(QuestionModel).count()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")

@router.get("/questions/random/{count}")
async def get_random_questions(
    count: int,
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """随机获取指定数量的题目（用于考试）"""
    query = db.query(QuestionModel)
    
    if category:
        query = query.filter(QuestionModel.category == category)
    
    all_questions = query.all()
    
    if len(all_questions) < count:
        raise HTTPException(
            status_code=400, 
            detail=f"题库中只有 {len(all_questions)} 道题目，无法抽取 {count} 道题目"
        )
    
    selected_questions = random.sample(all_questions, count)
    
    return selected_questions