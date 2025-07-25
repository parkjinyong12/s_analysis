"""
Sample 모델 정의
샘플 데이터를 관리하는 SQLAlchemy 모델
"""
from backend.extensions import db
from datetime import datetime
from typing import Dict, Any, Optional


class Sample(db.Model):
    """
    샘플 데이터 모델
    
    Attributes:
        id (int): 샘플 고유 ID (Primary Key)
        name (str): 샘플명 (최대 100자, 필수)
        description (str): 샘플 설명 (최대 255자, 선택)
        created_at (datetime): 생성 일시
    """
    __tablename__ = 'tb_sample'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, comment='샘플 고유 ID')
    
    # 샘플 정보
    name = db.Column(
        db.String(100), 
        nullable=False, 
        comment='샘플명'
    )
    description = db.Column(
        db.String(255), 
        comment='샘플 설명'
    )
    
    # 메타데이터
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        comment='생성 일시'
    )

    def __repr__(self) -> str:
        """객체 문자열 표현"""
        return f'<Sample {self.name}>'

    def to_dict(self) -> Dict[str, Any]:
        """
        Sample 객체를 딕셔너리로 변환 (API 응답용)
        
        Returns:
            Dict[str, Any]: 샘플 정보 딕셔너리
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_sample(cls, name: str, description: Optional[str] = None) -> 'Sample':
        """
        새 샘플 생성 (팩토리 메서드)
        
        Args:
            name (str): 샘플명
            description (Optional[str]): 샘플 설명
            
        Returns:
            Sample: 생성된 샘플 객체
        """
        return cls(name=name, description=description)
    
    def update_info(self, name: str, description: Optional[str] = None) -> None:
        """
        샘플 정보 업데이트
        
        Args:
            name (str): 새로운 샘플명
            description (Optional[str]): 새로운 샘플 설명
        """
        self.name = name
        if description is not None:
            self.description = description 