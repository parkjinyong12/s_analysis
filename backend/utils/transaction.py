# -*- coding: utf-8 -*-
"""
트랜잭션 관리 유틸리티
API 레벨에서 트랜잭션을 안전하게 관리하기 위한 데코레이터와 함수들을 제공합니다.
"""
import functools
import logging
from typing import Callable, Any
from flask import jsonify
from backend.extensions import db

logger = logging.getLogger(__name__)

def transactional(func: Callable) -> Callable:
    """
    트랜잭션을 관리하는 데코레이터
    
    함수 실행 중 예외가 발생하면 자동으로 rollback하고,
    성공적으로 완료되면 commit합니다.
    
    Args:
        func: 트랜잭션으로 관리할 함수
        
    Returns:
        데코레이터가 적용된 함수
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 성공 시 commit
            db.session.commit()
            logger.debug(f"트랜잭션 commit 성공: {func.__name__}")
            
            return result
            
        except Exception as e:
            # 실패 시 rollback
            db.session.rollback()
            logger.error(f"트랜잭션 rollback: {func.__name__} - {str(e)}")
            raise
    
    return wrapper

def safe_transaction(func: Callable) -> Callable:
    """
    안전한 트랜잭션 관리 데코레이터 (API 응답 포함)
    
    함수 실행 중 예외가 발생하면 rollback하고 적절한 HTTP 응답을 반환합니다.
    
    Args:
        func: 트랜잭션으로 관리할 함수
        
    Returns:
        데코레이터가 적용된 함수
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 성공 시 commit
            db.session.commit()
            logger.debug(f"트랜잭션 commit 성공: {func.__name__}")
            
            return result
            
        except ValueError as e:
            # 검증 오류 시 rollback
            db.session.rollback()
            logger.warning(f"트랜잭션 rollback (검증 오류): {func.__name__} - {str(e)}")
            return jsonify({
                'error': str(e),
                'type': 'validation_error'
            }), 400
            
        except Exception as e:
            # 기타 오류 시 rollback
            db.session.rollback()
            logger.error(f"트랜잭션 rollback (시스템 오류): {func.__name__} - {str(e)}")
            return jsonify({
                'error': '서버 내부 오류가 발생했습니다.',
                'type': 'system_error'
            }), 500
    
    return wrapper

def read_only_transaction(func: Callable) -> Callable:
    """
    읽기 전용 트랜잭션 데코레이터
    
    읽기 작업에 사용하며, 예외 발생 시에도 rollback하지 않습니다.
    
    Args:
        func: 읽기 전용 함수
        
    Returns:
        데코레이터가 적용된 함수
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"읽기 작업 실패: {func.__name__} - {str(e)}")
            raise
    
    return wrapper

def bulk_transaction(operations: list) -> bool:
    """
    여러 작업을 하나의 트랜잭션으로 처리
    
    Args:
        operations: 실행할 작업들의 리스트 (각각은 함수)
        
    Returns:
        bool: 모든 작업이 성공하면 True, 실패하면 False
    """
    try:
        for operation in operations:
            operation()
        
        db.session.commit()
        logger.info(f"벌크 트랜잭션 성공: {len(operations)}개 작업")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"벌크 트랜잭션 실패: {str(e)}")
        return False 