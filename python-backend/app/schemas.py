from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# 题库相关模式
class QuestionBase(BaseModel):
    category: str
    question_type: str = Field(alias="type")
    question: str
    option_a: str = Field(alias="optionA")
    option_b: str = Field(alias="optionB")
    option_c: Optional[str] = Field(alias="optionC", default=None)
    option_d: Optional[str] = Field(alias="optionD", default=None)
    answer: str
    explanation: Optional[str] = None
    question_id: Optional[int] = Field(alias="questionId", default=None)

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    category: Optional[str] = None
    question_type: Optional[str] = None
    question: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None

class Question(QuestionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# 考试记录相关模式
class ExamRecordBase(BaseModel):
    user_name: str = Field(alias="userName")
    user_id: Optional[str] = None
    department: Optional[str] = None
    region: Optional[str] = None
    score: int
    correct_count: int = Field(alias="correctCount")
    total_questions: int = Field(alias="totalQuestions")
    duration: int
    exam_type: str = "weekly"
    week_number: Optional[int] = None
    year: Optional[int] = None
    detailed_answers: Optional[Dict[str, Any]] = None
    ai_report: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class ExamRecordCreate(ExamRecordBase):
    id: str

class ExamRecord(ExamRecordBase):
    id: str
    created_at: datetime

# 题库数据结构（兼容现有格式）
class QuestionBank(BaseModel):
    version: int
    lastUpdate: str
    totalQuestions: int
    categories: List[str]
    maintainer: str = "管理员"
    questions: List[Question]
    # 考试相关字段（可选）
    exam_id: Optional[int] = None
    exam_name: Optional[str] = None
    duration_minutes: Optional[int] = None

# API配置模式
class APIConfig(BaseModel):
    provider: str = "qwen"
    url: str
    model: str = "qwen-turbo"
    key: str
    enabled: bool = True

class SystemConfigResponse(BaseModel):
    version: int
    lastUpdate: str
    apiConfig: APIConfig
    systemInfo: Dict[str, Any]
    permissions: Dict[str, bool]

# AI报告生成请求
class AIReportRequest(BaseModel):
    exam_record_id: str
    exam_data: Dict[str, Any]

class AIReportResponse(BaseModel):
    success: bool
    report: Optional[str] = None
    error: Optional[str] = None

# 考试管理相关模式
class ExamBase(BaseModel):
    exam_name: str
    description: Optional[str] = None
    exam_type: str = "formal"  # formal, practice
    duration_minutes: int = 20
    start_time: datetime
    end_time: datetime
    is_active: bool = True

class ExamCreate(ExamBase):
    question_ids: List[int]  # 选择的题目ID列表

class ExamUpdate(BaseModel):
    exam_name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    question_ids: Optional[List[int]] = None

class Exam(ExamBase):
    id: int
    created_by: str = "admin"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        orm_mode = True

class ExamWithQuestions(Exam):
    questions: List[Question]
    total_questions: int

class ExamList(BaseModel):
    id: int
    exam_name: str
    description: Optional[str]
    exam_type: str
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    is_active: bool
    total_questions: int
    status: str  # upcoming, active, expired
    
    class Config:
        from_attributes = True
        orm_mode = True

# 分析数据模式
class ExamAnalytics(BaseModel):
    total_exams: int
    avg_score: float
    high_performers: int
    low_performers: int
    department_stats: List[Dict[str, Any]]
    weekly_trends: List[Dict[str, Any]]