try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./exam_system.db")
    
    # API配置
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 通义千问API配置
    qwen_api_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
    qwen_model: str = "qwen-turbo"
    
    # 企业微信配置（暂时不用）
    wechat_corp_id: str = os.getenv("WECHAT_CORP_ID", "")
    wechat_secret: str = os.getenv("WECHAT_SECRET", "")
    
    class Config:
        env_file = ".env"

settings = Settings()