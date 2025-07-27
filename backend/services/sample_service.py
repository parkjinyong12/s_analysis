# -*- coding: utf-8 -*-
"""
Sample 서비스 계층
샘플 데이터 관련 비즈니스 로직을 처리하는 서비스
"""
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from backend.models.sample import Sample
from backend.extensions import db


class SampleService:
    """샘플 데이터 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    @staticmethod
    def create_sample(name: str, description: Optional[str] = None) -> Optional[Sample]:
        """
        새 샘플 생성
        
        Args:
            name (str): 샘플명
            description (Optional[str]): 샘플 설명
            
        Returns:
            Optional[Sample]: 생성된 샘플 객체 (실패 시 None)
            
        Raises:
            ValueError: 잘못된 입력값인 경우
        """
        try:
            # 입력값 검증
            if not name or not name.strip():
                raise ValueError("샘플명은 필수입니다.")
            
            # 샘플 생성
            sample = Sample.create_sample(name=name.strip(), description=description)
            db.session.add(sample)
            db.session.commit()
            
            return sample
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("데이터베이스 제약 조건 위반") from e
        except Exception as e:
            db.session.rollback()
            raise Exception(f"샘플 생성 중 오류 발생: {str(e)}") from e

    @staticmethod
    def get_all_samples() -> List[Sample]:
        """
        모든 샘플 조회
        
        Returns:
            List[Sample]: 샘플 목록 (생성일 기준 내림차순)
        """
        try:
            return Sample.query.order_by(Sample.created_at.desc()).all()
        except Exception as e:
            raise Exception(f"샘플 목록 조회 중 오류 발생: {str(e)}") from e

    @staticmethod
    def get_sample_by_id(sample_id: int) -> Optional[Sample]:
        """
        ID로 샘플 조회
        
        Args:
            sample_id (int): 샘플 ID
            
        Returns:
            Optional[Sample]: 샘플 객체 (없으면 None)
        """
        try:
            if sample_id <= 0:
                return None
            return Sample.query.get(sample_id)
        except Exception as e:
            raise Exception(f"샘플 조회 중 오류 발생: {str(e)}") from e

    @staticmethod
    def update_sample(sample_id: int, name: str, description: Optional[str] = None) -> Optional[Sample]:
        """
        샘플 정보 업데이트
        
        Args:
            sample_id (int): 샘플 ID
            name (str): 새로운 샘플명
            description (Optional[str]): 새로운 샘플 설명
            
        Returns:
            Optional[Sample]: 업데이트된 샘플 객체 (실패 시 None)
            
        Raises:
            ValueError: 잘못된 입력값인 경우
        """
        try:
            # 입력값 검증
            if not name or not name.strip():
                raise ValueError("샘플명은 필수입니다.")
            
            # 샘플 조회
            sample = Sample.query.get(sample_id)
            if not sample:
                return None
            
            # 정보 업데이트
            sample.update_info(name=name.strip(), description=description)
            db.session.commit()
            
            return sample
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"샘플 업데이트 중 오류 발생: {str(e)}") from e

    @staticmethod
    def delete_sample(sample_id: int) -> bool:
        """
        샘플 삭제
        
        Args:
            sample_id (int): 샘플 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            sample = Sample.query.get(sample_id)
            if not sample:
                return False
            
            db.session.delete(sample)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"샘플 삭제 중 오류 발생: {str(e)}") from e

    @staticmethod
    def search_samples_by_name(name: str) -> List[Sample]:
        """
        이름으로 샘플 검색
        
        Args:
            name (str): 검색할 이름 (부분 일치)
            
        Returns:
            List[Sample]: 검색된 샘플 목록
        """
        try:
            if not name or not name.strip():
                return []
            
            return Sample.query.filter(
                Sample.name.like(f'%{name.strip()}%')
            ).order_by(Sample.created_at.desc()).all()
            
        except Exception as e:
            raise Exception(f"샘플 검색 중 오류 발생: {str(e)}") from e


# 하위 호환성을 위한 함수들 (기존 코드와의 호환성 유지)
def create_sample(name: str, description: Optional[str] = None) -> Sample:
    """샘플 생성 (하위 호환성)"""
    result = SampleService.create_sample(name, description)
    if result is None:
        raise Exception("샘플 생성 실패")
    return result


def get_all_samples() -> List[Sample]:
    """모든 샘플 조회 (하위 호환성)"""
    return SampleService.get_all_samples()


def get_sample_by_id(sample_id: int) -> Optional[Sample]:
    """ID로 샘플 조회 (하위 호환성)"""
    return SampleService.get_sample_by_id(sample_id)


def update_sample(sample_id: int, name: str, description: Optional[str] = None) -> Optional[Sample]:
    """샘플 업데이트 (하위 호환성)"""
    return SampleService.update_sample(sample_id, name, description)


def delete_sample(sample_id: int) -> Optional[Sample]:
    """샘플 삭제 (하위 호환성)"""
    sample = SampleService.get_sample_by_id(sample_id)
    if sample and SampleService.delete_sample(sample_id):
        return sample
    return None 