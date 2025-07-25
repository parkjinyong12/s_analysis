import os
 
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': False,  # SQLite에서는 불필요
        'pool_recycle': -1,      # 연결 재사용 비활성화
        'connect_args': {
            'timeout': 60,       # 타임아웃 증가
            'check_same_thread': False,
            'isolation_level': None,  # autocommit 모드
        }
    } 