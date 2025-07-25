"""
User 서비스 계층
사용자 관련 비즈니스 로직을 처리하는 서비스
"""
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from backend.models.user import User
from backend.extensions import db


class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    @staticmethod
    def create_user(username: str, email: str) -> Optional[User]:
        """
        새 사용자 생성
        
        Args:
            username (str): 사용자명
            email (str): 이메일 주소
            
        Returns:
            Optional[User]: 생성된 사용자 객체 (실패 시 None)
            
        Raises:
            ValueError: 중복된 사용자명 또는 이메일인 경우
        """
        try:
            # 중복 체크
            if User.query.filter_by(username=username).first():
                raise ValueError(f"사용자명 '{username}'이 이미 존재합니다.")
            
            if User.query.filter_by(email=email).first():
                raise ValueError(f"이메일 '{email}'이 이미 존재합니다.")
            
            # 사용자 생성
            user = User.create_user(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            
            return user
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("데이터베이스 제약 조건 위반") from e
        except Exception as e:
            db.session.rollback()
            raise Exception(f"사용자 생성 중 오류 발생: {str(e)}") from e

    @staticmethod
    def get_all_users() -> List[User]:
        """
        모든 사용자 조회
        
        Returns:
            List[User]: 사용자 목록
        """
        try:
            return User.query.order_by(User.created_at.desc()).all()
        except Exception as e:
            raise Exception(f"사용자 목록 조회 중 오류 발생: {str(e)}") from e

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        ID로 사용자 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Optional[User]: 사용자 객체 (없으면 None)
        """
        try:
            return User.query.get(user_id)
        except Exception as e:
            raise Exception(f"사용자 조회 중 오류 발생: {str(e)}") from e

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        사용자명으로 사용자 조회
        
        Args:
            username (str): 사용자명
            
        Returns:
            Optional[User]: 사용자 객체 (없으면 None)
        """
        try:
            return User.query.filter_by(username=username).first()
        except Exception as e:
            raise Exception(f"사용자 조회 중 오류 발생: {str(e)}") from e


# 하위 호환성을 위한 함수들 (기존 코드와의 호환성 유지)
def create_user(username: str, email: str) -> User:
    """사용자 생성 (하위 호환성)"""
    result = UserService.create_user(username, email)
    if result is None:
        raise Exception("사용자 생성 실패")
    return result


def get_all_users() -> List[User]:
    """모든 사용자 조회 (하위 호환성)"""
    return UserService.get_all_users() 