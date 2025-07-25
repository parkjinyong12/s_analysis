"""
User 모델 정의
사용자 정보를 관리하는 SQLAlchemy 모델
"""
from backend.extensions import db
from datetime import datetime
from typing import Dict, Any


class User(db.Model):
    """
    사용자 정보 모델
    
    Attributes:
        id (int): 사용자 고유 ID (Primary Key)
        username (str): 사용자명 (최대 80자, 중복 불가)
        email (str): 이메일 주소 (최대 120자, 중복 불가)
        created_at (datetime): 생성 일시
    """
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, comment='사용자 고유 ID')
    
    # 사용자 정보
    username = db.Column(
        db.String(80), 
        unique=True, 
        nullable=False, 
        comment='사용자명'
    )
    email = db.Column(
        db.String(120), 
        unique=True, 
        nullable=False, 
        comment='이메일 주소'
    )
    
    # 메타데이터
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        comment='생성 일시'
    )

    def __repr__(self) -> str:
        """객체 문자열 표현"""
        return f'<User {self.username}>' 
    
    def to_dict(self) -> Dict[str, Any]:
        """
        User 객체를 딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 사용자 정보 딕셔너리
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_user(cls, username: str, email: str) -> 'User':
        """
        새 사용자 생성 (팩토리 메서드)
        
        Args:
            username (str): 사용자명
            email (str): 이메일 주소
            
        Returns:
            User: 생성된 사용자 객체
        """
        return cls(username=username, email=email) 