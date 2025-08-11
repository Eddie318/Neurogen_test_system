from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import QuestionBank, ProductTeam, Question, SystemConfig
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["question_banks"])

# Pydantic模型
class QuestionBankBase(BaseModel):
    team_id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True

class QuestionBankCreate(QuestionBankBase):
    pass

class QuestionBankUpdate(QuestionBankBase):
    pass

class QuestionBankResponse(QuestionBankBase):
    id: int
    created_at: datetime
    updated_at: datetime
    team_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        orm_mode = True

class QuestionBankWithStats(QuestionBankResponse):
    questions_count: int

class CurrentConfigResponse(BaseModel):
    current_team_id: int
    current_bank_id: int
    team_name: str
    bank_name: str

class AddQuestionToBankRequest(BaseModel):
    question_id: int

# 题库管理接口
@router.get("/question-banks", response_model=List[QuestionBankWithStats])
async def get_question_banks(team_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取题库列表（可按团队筛选）"""
    try:
        query = db.query(QuestionBank).join(ProductTeam).filter(QuestionBank.is_active == True)
        
        if team_id:
            query = query.filter(QuestionBank.team_id == team_id)
        
        banks = query.all()
        
        result = []
        for bank in banks:
            # 统计题目数量
            questions_count = db.query(Question).filter(
                Question.bank_id == bank.id
            ).count()
            
            bank_data = QuestionBankWithStats(
                id=bank.id,
                team_id=bank.team_id,
                name=bank.name,
                description=bank.description,
                is_active=bank.is_active,
                created_at=bank.created_at,
                updated_at=bank.updated_at,
                team_name=bank.team.name,
                questions_count=questions_count
            )
            result.append(bank_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题库列表失败: {str(e)}"
        )

@router.post("/question-banks", response_model=QuestionBankResponse)
async def create_question_bank(bank: QuestionBankCreate, db: Session = Depends(get_db)):
    """创建新题库"""
    try:
        # 检查团队是否存在
        team = db.query(ProductTeam).filter(ProductTeam.id == bank.team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定的团队不存在"
            )
        
        # 检查同一团队下题库名称是否重复
        existing_bank = db.query(QuestionBank).filter(
            QuestionBank.team_id == bank.team_id,
            QuestionBank.name == bank.name,
            QuestionBank.is_active == True
        ).first()
        if existing_bank:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"团队 '{team.name}' 下已存在名为 '{bank.name}' 的题库"
            )
        
        # 创建新题库
        db_bank = QuestionBank(
            team_id=bank.team_id,
            name=bank.name,
            description=bank.description,
            is_active=bank.is_active
        )
        
        db.add(db_bank)
        db.commit()
        db.refresh(db_bank)
        
        # 返回带团队名称的响应
        response = QuestionBankResponse.from_orm(db_bank)
        response.team_name = team.name
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建题库失败: {str(e)}"
        )

@router.get("/question-banks/{bank_id}", response_model=QuestionBankWithStats)
async def get_question_bank(bank_id: int, db: Session = Depends(get_db)):
    """获取单个题库详情"""
    try:
        bank = db.query(QuestionBank).join(ProductTeam).filter(QuestionBank.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题库不存在"
            )
        
        # 统计题目数量
        questions_count = db.query(Question).filter(Question.bank_id == bank.id).count()
        
        return QuestionBankWithStats(
            id=bank.id,
            team_id=bank.team_id,
            name=bank.name,
            description=bank.description,
            is_active=bank.is_active,
            created_at=bank.created_at,
            updated_at=bank.updated_at,
            team_name=bank.team.name,
            questions_count=questions_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题库详情失败: {str(e)}"
        )

@router.put("/question-banks/{bank_id}", response_model=QuestionBankResponse)
async def update_question_bank(bank_id: int, bank_update: QuestionBankUpdate, db: Session = Depends(get_db)):
    """更新题库信息"""
    try:
        bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题库不存在"
            )
        
        # 检查新团队是否存在
        if bank_update.team_id != bank.team_id:
            team = db.query(ProductTeam).filter(ProductTeam.id == bank_update.team_id).first()
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的团队不存在"
                )
        
        # 检查题库名称是否重复
        if bank_update.name != bank.name or bank_update.team_id != bank.team_id:
            existing_bank = db.query(QuestionBank).filter(
                QuestionBank.team_id == bank_update.team_id,
                QuestionBank.name == bank_update.name,
                QuestionBank.id != bank_id,
                QuestionBank.is_active == True
            ).first()
            if existing_bank:
                team = db.query(ProductTeam).filter(ProductTeam.id == bank_update.team_id).first()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"团队 '{team.name}' 下已存在名为 '{bank_update.name}' 的题库"
                )
        
        # 更新题库信息
        bank.team_id = bank_update.team_id
        bank.name = bank_update.name
        bank.description = bank_update.description
        bank.is_active = bank_update.is_active
        bank.updated_at = datetime.now()
        
        db.commit()
        db.refresh(bank)
        
        # 获取团队名称
        team = db.query(ProductTeam).filter(ProductTeam.id == bank.team_id).first()
        response = QuestionBankResponse.from_orm(bank)
        response.team_name = team.name if team else None
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新题库失败: {str(e)}"
        )

@router.delete("/question-banks/{bank_id}")
async def delete_question_bank(bank_id: int, db: Session = Depends(get_db)):
    """删除题库"""
    try:
        # 不允许删除默认题库
        if bank_id == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除默认题库"
            )
        
        bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题库不存在"
            )
        
        # 检查是否有关联的题目
        questions_count = db.query(Question).filter(Question.bank_id == bank_id).count()
        if questions_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该题库下还有 {questions_count} 道题目，无法删除"
            )
        
        # 软删除（设置为不活跃）
        bank.is_active = False
        bank.updated_at = datetime.now()
        
        db.commit()
        
        return {"success": True, "message": "题库删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除题库失败: {str(e)}"
        )

# 系统配置相关
@router.get("/current-config", response_model=CurrentConfigResponse)
async def get_current_config(db: Session = Depends(get_db)):
    """获取当前团队题库配置"""
    try:
        # 获取当前团队ID和题库ID
        team_config = db.query(SystemConfig).filter(SystemConfig.key == "current_team_id").first()
        bank_config = db.query(SystemConfig).filter(SystemConfig.key == "current_bank_id").first()
        
        current_team_id = int(team_config.value) if team_config else 1
        current_bank_id = int(bank_config.value) if bank_config else 1
        
        # 获取团队和题库名称
        team = db.query(ProductTeam).filter(ProductTeam.id == current_team_id).first()
        bank = db.query(QuestionBank).filter(QuestionBank.id == current_bank_id).first()
        
        return CurrentConfigResponse(
            current_team_id=current_team_id,
            current_bank_id=current_bank_id,
            team_name=team.name if team else "未知团队",
            bank_name=bank.name if bank else "未知题库"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取当前配置失败: {str(e)}"
        )

@router.post("/set-current-bank")
async def set_current_bank(team_id: int, bank_id: int, db: Session = Depends(get_db)):
    """设置当前使用的题库"""
    try:
        # 验证团队和题库是否存在且匹配
        team = db.query(ProductTeam).filter(ProductTeam.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定的团队不存在"
            )
        
        bank = db.query(QuestionBank).filter(
            QuestionBank.id == bank_id,
            QuestionBank.team_id == team_id,
            QuestionBank.is_active == True
        ).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定的题库不存在或不属于该团队"
            )
        
        # 更新系统配置
        current_time = datetime.now().isoformat()
        
        # 更新当前团队ID
        team_config = db.query(SystemConfig).filter(SystemConfig.key == "current_team_id").first()
        if team_config:
            team_config.value = str(team_id)
            team_config.updated_at = datetime.now()
        else:
            team_config = SystemConfig(
                key="current_team_id",
                value=str(team_id),
                description="当前活动的团队ID",
                config_type="number"
            )
            db.add(team_config)
        
        # 更新当前题库ID
        bank_config = db.query(SystemConfig).filter(SystemConfig.key == "current_bank_id").first()
        if bank_config:
            bank_config.value = str(bank_id)
            bank_config.updated_at = datetime.now()
        else:
            bank_config = SystemConfig(
                key="current_bank_id",
                value=str(bank_id),
                description="当前活动的题库ID",
                config_type="number"
            )
            db.add(bank_config)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"已设置当前题库为：{team.name} - {bank.name}",
            "team_id": team_id,
            "bank_id": bank_id,
            "team_name": team.name,
            "bank_name": bank.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"设置当前题库失败: {str(e)}"
        )

@router.post("/question-banks/{bank_id}/questions")
async def add_question_to_bank(bank_id: int, request: AddQuestionToBankRequest, db: Session = Depends(get_db)):
    """将题目添加到指定题库"""
    try:
        # 检查题库是否存在
        bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题库不存在"
            )
        
        # 检查源题目是否存在（从questions表的默认题库bank_id=1中获取）
        source_question = db.query(Question).filter(
            Question.id == request.question_id
        ).first()
        
        if not source_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="源题目不存在"
            )
        
        # 检查题目是否已经在该题库中
        existing_question = db.query(Question).filter(
            Question.bank_id == bank_id,
            Question.question == source_question.question
        ).first()
        
        if existing_question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该题目已经在题库中"
            )
        
        # 将题目复制到目标题库中
        new_question = Question(
            bank_id=bank_id,
            category=source_question.category,
            question_type=source_question.question_type,
            question=source_question.question,
            option_a=source_question.option_a,
            option_b=source_question.option_b,
            option_c=source_question.option_c,
            option_d=source_question.option_d,
            answer=source_question.answer,
            explanation=source_question.explanation or ""
        )
        
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        
        return {
            "success": True,
            "message": "题目添加到题库成功",
            "question_id": new_question.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加题目到题库失败: {str(e)}"
        )

@router.get("/question-banks/{bank_id}/questions")
async def get_bank_questions(bank_id: int, db: Session = Depends(get_db)):
    """获取指定题库的所有题目"""
    try:
        # 检查题库是否存在
        bank = db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题库不存在"
            )
        
        # 获取题库中的所有题目
        questions = db.query(Question).filter(Question.bank_id == bank_id).all()
        
        result = []
        for question in questions:
            result.append({
                "id": question.id,
                "category": question.category,
                "question_type": question.question_type,
                "question": question.question,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d,
                "answer": question.answer,
                "explanation": question.explanation,
                "created_at": question.created_at,
                "updated_at": question.updated_at
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题库题目失败: {str(e)}"
        )