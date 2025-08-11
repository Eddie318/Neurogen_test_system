from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import ProductTeam, QuestionBank, Question, ExamRecord
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["teams"])

# Pydantic模型
class TeamBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        orm_mode = True

class TeamWithStats(TeamResponse):
    banks_count: int
    questions_count: int
    exams_count: int

# 团队管理接口
@router.get("/teams", response_model=List[TeamWithStats])
async def get_teams(db: Session = Depends(get_db)):
    """获取所有团队列表（带统计信息）"""
    try:
        # 获取团队基本信息
        teams = db.query(ProductTeam).filter(ProductTeam.is_active == True).all()
        
        result = []
        for team in teams:
            # 统计每个团队的题库、题目、考试数量
            banks_count = db.query(QuestionBank).filter(
                QuestionBank.team_id == team.id,
                QuestionBank.is_active == True
            ).count()
            
            questions_count = db.query(Question).join(QuestionBank).filter(
                QuestionBank.team_id == team.id,
                QuestionBank.is_active == True
            ).count()
            
            exams_count = db.query(ExamRecord).filter(
                ExamRecord.team_id == team.id
            ).count()
            
            team_data = TeamWithStats(
                id=team.id,
                name=team.name,
                code=team.code,
                description=team.description,
                is_active=team.is_active,
                created_at=team.created_at,
                updated_at=team.updated_at,
                banks_count=banks_count,
                questions_count=questions_count,
                exams_count=exams_count
            )
            result.append(team_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取团队列表失败: {str(e)}"
        )

@router.post("/teams", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """创建新团队"""
    try:
        # 检查团队代码是否重复
        existing_team = db.query(ProductTeam).filter(ProductTeam.code == team.code).first()
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"团队代码 '{team.code}' 已存在"
            )
        
        # 创建新团队
        db_team = ProductTeam(
            name=team.name,
            code=team.code,
            description=team.description,
            is_active=team.is_active
        )
        
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        
        return TeamResponse.from_orm(db_team)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建团队失败: {str(e)}"
        )

@router.get("/teams/{team_id}", response_model=TeamWithStats)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """获取单个团队详情"""
    try:
        team = db.query(ProductTeam).filter(ProductTeam.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="团队不存在"
            )
        
        # 统计信息
        banks_count = db.query(QuestionBank).filter(
            QuestionBank.team_id == team.id,
            QuestionBank.is_active == True
        ).count()
        
        questions_count = db.query(Question).join(QuestionBank).filter(
            QuestionBank.team_id == team.id,
            QuestionBank.is_active == True
        ).count()
        
        exams_count = db.query(ExamRecord).filter(
            ExamRecord.team_id == team.id
        ).count()
        
        return TeamWithStats(
            id=team.id,
            name=team.name,
            code=team.code,
            description=team.description,
            is_active=team.is_active,
            created_at=team.created_at,
            updated_at=team.updated_at,
            banks_count=banks_count,
            questions_count=questions_count,
            exams_count=exams_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取团队详情失败: {str(e)}"
        )

@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(team_id: int, team_update: TeamUpdate, db: Session = Depends(get_db)):
    """更新团队信息"""
    try:
        team = db.query(ProductTeam).filter(ProductTeam.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="团队不存在"
            )
        
        # 检查团队代码是否与其他团队重复
        if team_update.code != team.code:
            existing_team = db.query(ProductTeam).filter(
                ProductTeam.code == team_update.code,
                ProductTeam.id != team_id
            ).first()
            if existing_team:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"团队代码 '{team_update.code}' 已存在"
                )
        
        # 更新团队信息
        team.name = team_update.name
        team.code = team_update.code
        team.description = team_update.description
        team.is_active = team_update.is_active
        team.updated_at = datetime.now()
        
        db.commit()
        db.refresh(team)
        
        return TeamResponse.from_orm(team)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新团队失败: {str(e)}"
        )

@router.delete("/teams/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    """删除团队"""
    try:
        # 不允许删除默认团队
        if team_id == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除默认团队"
            )
        
        team = db.query(ProductTeam).filter(ProductTeam.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="团队不存在"
            )
        
        # 检查是否有关联的题库
        banks_count = db.query(QuestionBank).filter(QuestionBank.team_id == team_id).count()
        if banks_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该团队下还有 {banks_count} 个题库，无法删除"
            )
        
        # 软删除（设置为不活跃）
        team.is_active = False
        team.updated_at = datetime.now()
        
        db.commit()
        
        return {"success": True, "message": "团队删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除团队失败: {str(e)}"
        )