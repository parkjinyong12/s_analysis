# -*- coding: utf-8 -*-
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
        'pool_pre_ping': True,           # PostgreSQL 연결 상태 확인
        'pool_recycle': 1800,            # 30분마다 연결 재생성 (더 짧게)
        'pool_size': 5,                  # 연결 풀 크기 (더 작게)
        'max_overflow': 10,              # 최대 추가 연결 수 (더 작게)
        'pool_timeout': 30,              # 연결 대기 시간
        'connect_args': {
            'connect_timeout': 10,       # 연결 타임아웃
            'application_name': 'stock_analysis',  # 애플리케이션 이름
            'keepalives_idle': 30,       # keepalive 설정
            'keepalives_interval': 10,
            'keepalives_count': 5,
        }
    }
    
    # 장시간 배치 처리를 위한 설정
    BATCH_PROCESSING = {
        'max_workers': 2,                # 최대 워커 수 (메모리 절약)
        'task_timeout': 3600,            # 작업 타임아웃 (1시간)
        'heartbeat_interval': 300,       # 하트비트 간격 (5분)
        'max_memory_usage': 80,          # 최대 메모리 사용률 (%)
        'auto_restart_on_failure': True, # 실패 시 자동 재시작
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 테스트 모드 설정
    TESTING = os.environ.get('TESTING', 'false').lower() == 'true'
    TEST_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    if not TEST_DATABASE_URI:
        raise ValueError("TEST_DATABASE_URL 환경변수가 설정되지 않았습니다. 테스트용 PostgreSQL 연결 정보를 설정해주세요.") 