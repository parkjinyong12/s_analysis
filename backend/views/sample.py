"""
Sample REST API 뷰
샘플 데이터에 대한 CRUD API 엔드포인트를 제공합니다.
"""
from flask import Blueprint, jsonify, request
from backend.services.sample_service import SampleService
from backend.utils.transaction import safe_transaction, read_only_transaction
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
sample_bp = Blueprint('sample', __name__, url_prefix='/samples')


@sample_bp.route('/', methods=['GET'])
@read_only_transaction
def list_samples():
    """
    샘플 목록 조회
    
    Returns:
        JSON: 샘플 목록 배열
        
    Example:
        GET /samples/
        Response: [{"id": 1, "name": "Sample 1", "description": "Description", "created_at": "2024-01-01T00:00:00"}]
    """
    try:
        samples = SampleService.get_all_samples()
        return jsonify([sample.to_dict() for sample in samples]), 200
        
    except Exception as e:
        logger.error(f"샘플 목록 조회 실패: {str(e)}")
        return jsonify({
            'error': '샘플 목록을 조회하는데 실패했습니다.',
            'message': str(e)
        }), 500


@sample_bp.route('/<int:sample_id>', methods=['GET'])
@read_only_transaction
def get_sample(sample_id):
    """
    특정 샘플 조회
    
    Args:
        sample_id (int): 샘플 ID
        
    Returns:
        JSON: 샘플 정보 또는 에러 메시지
        
    Example:
        GET /samples/1
        Response: {"id": 1, "name": "Sample 1", "description": "Description", "created_at": "2024-01-01T00:00:00"}
    """
    try:
        # 입력값 검증
        if sample_id <= 0:
            return jsonify({
                'error': '유효하지 않은 샘플 ID입니다.',
                'sample_id': sample_id
            }), 400
        
        sample = SampleService.get_sample_by_id(sample_id)
        
        if not sample:
            return jsonify({
                'error': '샘플을 찾을 수 없습니다.',
                'sample_id': sample_id
            }), 404
            
        return jsonify(sample.to_dict()), 200
        
    except Exception as e:
        logger.error(f"샘플 조회 실패 (ID: {sample_id}): {str(e)}")
        return jsonify({
            'error': '샘플을 조회하는데 실패했습니다.',
            'message': str(e)
        }), 500


@sample_bp.route('/', methods=['POST'])
@safe_transaction
def create_sample_api():
    """
    새 샘플 생성
    
    Request Body:
        name (str): 샘플명 (필수)
        description (str): 샘플 설명 (선택)
        
    Returns:
        JSON: 생성된 샘플 정보
        
    Example:
        POST /samples/
        Body: {"name": "New Sample", "description": "Sample description"}
        Response: {"id": 1, "name": "New Sample", "description": "Sample description", "created_at": "2024-01-01T00:00:00"}
    """
    try:
        # 요청 데이터 검증
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type은 application/json이어야 합니다.'
            }), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': '요청 본문이 비어있습니다.'
            }), 400
        
        # 필수 필드 검증
        name = data.get('name')
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({
                'error': '샘플명은 필수이며 비어있을 수 없습니다.',
                'field': 'name'
            }), 400
        
        description = data.get('description')
        if description is not None and not isinstance(description, str):
            return jsonify({
                'error': '설명은 문자열이어야 합니다.',
                'field': 'description'
            }), 400
        
        # 샘플 생성
        sample = SampleService.create_sample(
            name=name.strip(),
            description=description.strip() if description else None
        )
        
        if not sample:
            return jsonify({
                'error': '샘플 생성에 실패했습니다.'
            }), 500
        
        logger.info(f"새 샘플 생성됨: {sample.name} (ID: {sample.id})")
        return jsonify(sample.to_dict()), 201
        
    except ValueError as e:
        logger.warning(f"샘플 생성 입력값 오류: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"샘플 생성 실패: {str(e)}")
        return jsonify({
            'error': '샘플을 생성하는데 실패했습니다.',
            'message': str(e)
        }), 500


@sample_bp.route('/<int:sample_id>', methods=['PUT'])
@safe_transaction
def update_sample_api(sample_id):
    """
    샘플 정보 수정
    
    Args:
        sample_id (int): 샘플 ID
        
    Request Body:
        name (str): 샘플명 (필수)
        description (str): 샘플 설명 (선택)
        
    Returns:
        JSON: 수정된 샘플 정보
        
    Example:
        PUT /samples/1
        Body: {"name": "Updated Sample", "description": "Updated description"}
        Response: {"id": 1, "name": "Updated Sample", "description": "Updated description", "created_at": "2024-01-01T00:00:00"}
    """
    try:
        # 입력값 검증
        if sample_id <= 0:
            return jsonify({
                'error': '유효하지 않은 샘플 ID입니다.',
                'sample_id': sample_id
            }), 400
        
        # 요청 데이터 검증
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type은 application/json이어야 합니다.'
            }), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': '요청 본문이 비어있습니다.'
            }), 400
        
        # 필수 필드 검증
        name = data.get('name')
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({
                'error': '샘플명은 필수이며 비어있을 수 없습니다.',
                'field': 'name'
            }), 400
        
        description = data.get('description')
        if description is not None and not isinstance(description, str):
            return jsonify({
                'error': '설명은 문자열이어야 합니다.',
                'field': 'description'
            }), 400
        
        # 샘플 수정
        sample = SampleService.update_sample(
            sample_id=sample_id,
            name=name.strip(),
            description=description.strip() if description else None
        )
        
        if not sample:
            return jsonify({
                'error': '샘플을 찾을 수 없습니다.',
                'sample_id': sample_id
            }), 404
        
        logger.info(f"샘플 수정됨: {sample.name} (ID: {sample.id})")
        return jsonify(sample.to_dict()), 200
        
    except ValueError as e:
        logger.warning(f"샘플 수정 입력값 오류 (ID: {sample_id}): {str(e)}")
        return jsonify({
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"샘플 수정 실패 (ID: {sample_id}): {str(e)}")
        return jsonify({
            'error': '샘플을 수정하는데 실패했습니다.',
            'message': str(e)
        }), 500


@sample_bp.route('/<int:sample_id>', methods=['DELETE'])
@safe_transaction
def delete_sample_api(sample_id):
    """
    샘플 삭제
    
    Args:
        sample_id (int): 샘플 ID
        
    Returns:
        JSON: 삭제 결과 메시지
        
    Example:
        DELETE /samples/1
        Response: {"result": "success", "message": "샘플이 성공적으로 삭제되었습니다.", "sample_id": 1}
    """
    try:
        # 입력값 검증
        if sample_id <= 0:
            return jsonify({
                'error': '유효하지 않은 샘플 ID입니다.',
                'sample_id': sample_id
            }), 400
        
        # 삭제 전 샘플 존재 확인
        existing_sample = SampleService.get_sample_by_id(sample_id)
        if not existing_sample:
            return jsonify({
                'error': '샘플을 찾을 수 없습니다.',
                'sample_id': sample_id
            }), 404
        
        # 샘플 삭제
        success = SampleService.delete_sample(sample_id)
        
        if not success:
            return jsonify({
                'error': '샘플 삭제에 실패했습니다.',
                'sample_id': sample_id
            }), 500
        
        logger.info(f"샘플 삭제됨: {existing_sample.name} (ID: {sample_id})")
        return jsonify({
            'result': 'success',
            'message': '샘플이 성공적으로 삭제되었습니다.',
            'sample_id': sample_id
        }), 200
        
    except Exception as e:
        logger.error(f"샘플 삭제 실패 (ID: {sample_id}): {str(e)}")
        return jsonify({
            'error': '샘플을 삭제하는데 실패했습니다.',
            'message': str(e)
        }), 500


@sample_bp.route('/search', methods=['GET'])
@read_only_transaction
def search_samples():
    """
    샘플 검색
    
    Query Parameters:
        name (str): 검색할 이름 (부분 일치)
        
    Returns:
        JSON: 검색된 샘플 목록
        
    Example:
        GET /samples/search?name=test
        Response: [{"id": 1, "name": "Test Sample", "description": "Description", "created_at": "2024-01-01T00:00:00"}]
    """
    try:
        name = request.args.get('name', '').strip()
        
        if not name:
            return jsonify({
                'error': '검색할 이름을 입력해주세요.',
                'parameter': 'name'
            }), 400
        
        samples = SampleService.search_samples_by_name(name)
        return jsonify([sample.to_dict() for sample in samples]), 200
        
    except Exception as e:
        logger.error(f"샘플 검색 실패 (name: {name}): {str(e)}")
        return jsonify({
            'error': '샘플을 검색하는데 실패했습니다.',
            'message': str(e)
        }), 500


# 에러 핸들러
@sample_bp.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        'error': '요청한 리소스를 찾을 수 없습니다.',
        'status_code': 404
    }), 404


@sample_bp.errorhandler(405)
def method_not_allowed(error):
    """405 에러 핸들러"""
    return jsonify({
        'error': '허용되지 않은 HTTP 메서드입니다.',
        'status_code': 405
    }), 405


@sample_bp.errorhandler(500)
def internal_server_error(error):
    """500 에러 핸들러"""
    logger.error(f"내부 서버 오류: {str(error)}")
    return jsonify({
        'error': '내부 서버 오류가 발생했습니다.',
        'status_code': 500
    }), 500 