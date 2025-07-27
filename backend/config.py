import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
 
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey')
    
    # PostgreSQL 설정
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다. PostgreSQL 연결 정보를 설정해주세요.")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,   # PostgreSQL 연결 상태 확인
        'pool_recycle': 3600,    # 1시간마다 연결 재생성
        'pool_size': 10,         # 연결 풀 크기
        'max_overflow': 20,      # 최대 추가 연결 수
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 테스트 모드 설정
    TESTING = os.environ.get('TESTING', 'false').lower() == 'true'
    TEST_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    if not TEST_DATABASE_URI:
        raise ValueError("TEST_DATABASE_URL 환경변수가 설정되지 않았습니다. 테스트용 PostgreSQL 연결 정보를 설정해주세요.") 