from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class ProductTeam(Base):
    """产品团队表"""
    __tablename__ = "product_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    # 预留企业微信字段
    wechat_dept_id = Column(String(100))
    wechat_mapping = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    question_banks = relationship("QuestionBank", back_populates="team")

class QuestionBank(Base):
    """题库表"""
    __tablename__ = "question_banks"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("product_teams.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    team = relationship("ProductTeam", back_populates="question_banks")
    questions = relationship("Question", back_populates="question_bank")

class Question(Base):
    """题库表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey("question_banks.id"), nullable=False, default=1, index=True)
    category = Column(String(100), nullable=False, index=True)
    question_type = Column(String(20), nullable=False)  # single, multiple
    question = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text)
    option_d = Column(Text)
    answer = Column(String(10), nullable=False)
    explanation = Column(Text)
    question_id = Column(Integer)  # 原题目ID，用于兼容
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    question_bank = relationship("QuestionBank", back_populates="questions")

class ExamRecord(Base):
    """考试记录表"""
    __tablename__ = "exam_records"
    
    id = Column(String(100), primary_key=True)
    user_name = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), index=True)  # 企业微信用户ID，暂时可为空
    team_id = Column(Integer, ForeignKey("product_teams.id"), default=1, index=True)
    bank_id = Column(Integer, ForeignKey("question_banks.id"), default=1, index=True)
    department = Column(String(100), index=True)
    region = Column(String(100))
    score = Column(Integer, nullable=False, index=True)
    correct_count = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # 考试用时（秒）
    exam_type = Column(String(50), default="weekly")  # 考试类型
    week_number = Column(Integer, index=True)
    year = Column(Integer, index=True)
    detailed_answers = Column(JSON)  # 详细答题数据
    questions_data = Column(JSON)  # 完整题目数据（用于AI分析）
    ai_report = Column(Text)  # AI分析报告
    created_at = Column(DateTime, server_default=func.now(), index=True)

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)
    description = Column(String(500))
    config_type = Column(String(50), default="string")  # string, json, number, boolean
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class User(Base):
    """用户表（可选，暂时不用）"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)  # 企业微信用户ID
    username = Column(String(100), unique=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    region = Column(String(100))
    role = Column(String(20), default="sales")  # sales, admin, sfe
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)

class Exam(Base):
    """考试表"""
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    exam_type = Column(String(50), default="formal")  # formal(正式考试), practice(随机练习)
    duration_minutes = Column(Integer, default=20)  # 考试时长（分钟）
    start_time = Column(DateTime, nullable=False, index=True)  # 考试开始时间
    end_time = Column(DateTime, nullable=False, index=True)    # 考试结束时间
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(String(100), default="admin")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    exam_questions = relationship("ExamQuestion", back_populates="exam")

class ExamQuestion(Base):
    """考试-题目关联表"""
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    order_index = Column(Integer, default=1)  # 题目在考试中的顺序
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联关系
    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question")