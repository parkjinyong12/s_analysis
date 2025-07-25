"""
Stock REST API 뷰
주식 목록에 대한 CRUD API 엔드포인트를 제공합니다.
"""
from flask import Blueprint, jsonify, request
from backend.services.stock_service import StockService
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
stock_bp = Blueprint('stock', __name__, url_prefix='/stocks')


@stock_bp.route('/', methods=['GET'])
def list_stocks():
    """
    주식 목록 조회
    
    Returns:
        JSON: 주식 목록 배열
        
    Example:
        GET /stocks/
        Response: [{"id": 1, "stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 0, "foreigner_accum_init": 0}]
    """
    try:
        stocks = StockService.get_all_stocks()
        return jsonify([stock.to_dict() for stock in stocks]), 200
        
    except Exception as e:
        logger.error(f"주식 목록 조회 실패: {str(e)}")
        return jsonify({
            'error': '주식 목록을 조회하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/<int:stock_id>', methods=['GET'])
def get_stock(stock_id):
    """
    특정 주식 조회
    
    Args:
        stock_id (int): 주식 ID
        
    Returns:
        JSON: 주식 정보 또는 에러 메시지
        
    Example:
        GET /stocks/1
        Response: {"id": 1, "stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 0, "foreigner_accum_init": 0}
    """
    try:
        # 입력값 검증
        if stock_id <= 0:
            return jsonify({
                'error': '유효하지 않은 주식 ID입니다.',
                'stock_id': stock_id
            }), 400
        
        stock = StockService.get_stock_by_id(stock_id)
        
        if not stock:
            return jsonify({
                'error': '주식을 찾을 수 없습니다.',
                'stock_id': stock_id
            }), 404
            
        return jsonify(stock.to_dict()), 200
        
    except Exception as e:
        logger.error(f"주식 조회 실패 (ID: {stock_id}): {str(e)}")
        return jsonify({
            'error': '주식을 조회하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/code/<string:stock_code>', methods=['GET'])
def get_stock_by_code(stock_code):
    """
    주식 코드로 주식 조회
    
    Args:
        stock_code (str): 주식 코드
        
    Returns:
        JSON: 주식 정보 또는 에러 메시지
        
    Example:
        GET /stocks/code/005930
        Response: {"id": 1, "stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 0, "foreigner_accum_init": 0}
    """
    try:
        # 입력값 검증
        if not stock_code or not stock_code.strip():
            return jsonify({
                'error': '주식 코드는 필수입니다.',
                'stock_code': stock_code
            }), 400
        
        stock = StockService.get_stock_by_code(stock_code.strip())
        
        if not stock:
            return jsonify({
                'error': '주식을 찾을 수 없습니다.',
                'stock_code': stock_code
            }), 404
            
        return jsonify(stock.to_dict()), 200
        
    except Exception as e:
        logger.error(f"주식 조회 실패 (Code: {stock_code}): {str(e)}")
        return jsonify({
            'error': '주식을 조회하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/', methods=['POST'])
def create_stock_api():
    """
    새 주식 생성
    
    Request Body:
        stock_code (str): 주식 코드 (필수, 6자리 숫자, 최대 20자)
        stock_name (str): 주식명 (필수, 최대 100자)
        init_date (str): 초기화 날짜 (선택, YYYY-MM-DD 형식, 최대 10자)
        institution_accum_init (int): 기관 누적 초기값 (선택, 기본값: 0, 0 이상)
        foreigner_accum_init (int): 외국인 누적 초기값 (선택, 기본값: 0, 0 이상)
        
    Returns:
        JSON: 생성된 주식 정보
        
    Example:
        POST /stocks/
        Body: {"stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 1000, "foreigner_accum_init": 2000}
        Response: {"id": 1, "stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 1000, "foreigner_accum_init": 2000}
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
        stock_code = data.get('stock_code')
        if not stock_code or not isinstance(stock_code, str) or not stock_code.strip():
            return jsonify({
                'error': '주식 코드는 필수이며 비어있을 수 없습니다.',
                'field': 'stock_code',
                'constraints': '6자리 숫자, 최대 20자'
            }), 400
        
        stock_name = data.get('stock_name')
        if not stock_name or not isinstance(stock_name, str) or not stock_name.strip():
            return jsonify({
                'error': '주식명은 필수이며 비어있을 수 없습니다.',
                'field': 'stock_name',
                'constraints': '최대 100자'
            }), 400
        
        # 선택 필드 검증
        init_date = data.get('init_date')
        if init_date is not None and not isinstance(init_date, str):
            return jsonify({
                'error': '초기화 날짜는 문자열이어야 합니다.',
                'field': 'init_date',
                'constraints': 'YYYY-MM-DD 형식, 최대 10자'
            }), 400
        
        institution_accum_init = data.get('institution_accum_init', 0)
        if not isinstance(institution_accum_init, int):
            return jsonify({
                'error': '기관 누적 초기값은 정수여야 합니다.',
                'field': 'institution_accum_init',
                'constraints': '0 이상의 정수'
            }), 400
        
        foreigner_accum_init = data.get('foreigner_accum_init', 0)
        if not isinstance(foreigner_accum_init, int):
            return jsonify({
                'error': '외국인 누적 초기값은 정수여야 합니다.',
                'field': 'foreigner_accum_init',
                'constraints': '0 이상의 정수'
            }), 400
        
        # 주식 생성
        stock = StockService.create_stock(
            stock_code=stock_code.strip(),
            stock_name=stock_name.strip(),
            init_date=init_date.strip() if init_date else None,
            institution_accum_init=institution_accum_init,
            foreigner_accum_init=foreigner_accum_init
        )
        
        if not stock:
            return jsonify({
                'error': '주식 생성에 실패했습니다.'
            }), 500
        
        logger.info(f"새 주식 생성됨: {stock.stock_code} - {stock.stock_name} (ID: {stock.id})")
        return jsonify(stock.to_dict()), 201
        
    except ValueError as e:
        logger.warning(f"주식 생성 입력값 오류: {str(e)}")
        return jsonify({
            'error': str(e),
            'type': 'validation_error'
        }), 400
        
    except Exception as e:
        logger.error(f"주식 생성 실패: {str(e)}")
        return jsonify({
            'error': '주식을 생성하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/<int:stock_id>', methods=['PUT'])
def update_stock_api(stock_id):
    """
    주식 정보 수정
    
    Args:
        stock_id (int): 주식 ID
        
    Request Body:
        stock_name (str): 주식명 (필수, 최대 100자)
        init_date (str): 초기화 날짜 (선택, YYYY-MM-DD 형식, 최대 10자)
        institution_accum_init (int): 기관 누적 초기값 (선택, 0 이상)
        foreigner_accum_init (int): 외국인 누적 초기값 (선택, 0 이상)
        
    Returns:
        JSON: 수정된 주식 정보
        
    Example:
        PUT /stocks/1
        Body: {"stock_name": "삼성전자우", "init_date": "2024-01-02", "institution_accum_init": 1500, "foreigner_accum_init": 2500}
        Response: {"id": 1, "stock_code": "005930", "stock_name": "삼성전자우", "init_date": "2024-01-02", "institution_accum_init": 1500, "foreigner_accum_init": 2500}
    """
    try:
        # 입력값 검증
        if stock_id <= 0:
            return jsonify({
                'error': '유효하지 않은 주식 ID입니다.',
                'stock_id': stock_id
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
        stock_name = data.get('stock_name')
        if not stock_name or not isinstance(stock_name, str) or not stock_name.strip():
            return jsonify({
                'error': '주식명은 필수이며 비어있을 수 없습니다.',
                'field': 'stock_name',
                'constraints': '최대 100자'
            }), 400
        
        # 선택 필드 검증
        init_date = data.get('init_date')
        if init_date is not None and not isinstance(init_date, str):
            return jsonify({
                'error': '초기화 날짜는 문자열이어야 합니다.',
                'field': 'init_date',
                'constraints': 'YYYY-MM-DD 형식, 최대 10자'
            }), 400
        
        institution_accum_init = data.get('institution_accum_init')
        if institution_accum_init is not None and not isinstance(institution_accum_init, int):
            return jsonify({
                'error': '기관 누적 초기값은 정수여야 합니다.',
                'field': 'institution_accum_init',
                'constraints': '0 이상의 정수'
            }), 400
        
        foreigner_accum_init = data.get('foreigner_accum_init')
        if foreigner_accum_init is not None and not isinstance(foreigner_accum_init, int):
            return jsonify({
                'error': '외국인 누적 초기값은 정수여야 합니다.',
                'field': 'foreigner_accum_init',
                'constraints': '0 이상의 정수'
            }), 400
        
        # 주식 수정
        stock = StockService.update_stock(
            stock_id=stock_id,
            stock_name=stock_name.strip(),
            init_date=init_date.strip() if init_date else None,
            institution_accum_init=institution_accum_init,
            foreigner_accum_init=foreigner_accum_init
        )
        
        if not stock:
            return jsonify({
                'error': '주식을 찾을 수 없습니다.',
                'stock_id': stock_id
            }), 404
        
        logger.info(f"주식 수정됨: {stock.stock_code} - {stock.stock_name} (ID: {stock.id})")
        return jsonify(stock.to_dict()), 200
        
    except ValueError as e:
        logger.warning(f"주식 수정 입력값 오류 (ID: {stock_id}): {str(e)}")
        return jsonify({
            'error': str(e),
            'type': 'validation_error'
        }), 400
        
    except Exception as e:
        logger.error(f"주식 수정 실패 (ID: {stock_id}): {str(e)}")
        return jsonify({
            'error': '주식을 수정하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/<int:stock_id>', methods=['DELETE'])
def delete_stock_api(stock_id):
    """
    주식 삭제
    
    Args:
        stock_id (int): 주식 ID
        
    Returns:
        JSON: 삭제 결과 메시지
        
    Example:
        DELETE /stocks/1
        Response: {"result": "success", "message": "주식이 성공적으로 삭제되었습니다.", "stock_id": 1}
    """
    try:
        # 입력값 검증
        if stock_id <= 0:
            return jsonify({
                'error': '유효하지 않은 주식 ID입니다.',
                'stock_id': stock_id
            }), 400
        
        # 삭제 전 주식 존재 확인
        existing_stock = StockService.get_stock_by_id(stock_id)
        if not existing_stock:
            return jsonify({
                'error': '주식을 찾을 수 없습니다.',
                'stock_id': stock_id
            }), 404
        
        # 주식 삭제
        success = StockService.delete_stock(stock_id)
        
        if not success:
            return jsonify({
                'error': '주식 삭제에 실패했습니다.',
                'stock_id': stock_id
            }), 500
        
        logger.info(f"주식 삭제됨: {existing_stock.stock_code} - {existing_stock.stock_name} (ID: {stock_id})")
        return jsonify({
            'result': 'success',
            'message': '주식이 성공적으로 삭제되었습니다.',
            'stock_id': stock_id
        }), 200
        
    except Exception as e:
        logger.error(f"주식 삭제 실패 (ID: {stock_id}): {str(e)}")
        return jsonify({
            'error': '주식을 삭제하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/search', methods=['GET'])
def search_stocks():
    """
    주식 검색
    
    Query Parameters:
        name (str): 검색할 주식명 (부분 일치)
        code (str): 검색할 주식 코드 (부분 일치)
        
    Returns:
        JSON: 검색된 주식 목록
        
    Example:
        GET /stocks/search?name=삼성
        GET /stocks/search?code=005
        Response: [{"id": 1, "stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 0, "foreigner_accum_init": 0}]
    """
    try:
        name = request.args.get('name', '').strip()
        code = request.args.get('code', '').strip()
        
        if not name and not code:
            return jsonify({
                'error': '검색할 주식명 또는 주식 코드를 입력해주세요.',
                'parameters': ['name', 'code']
            }), 400
        
        stocks = []
        if name:
            stocks.extend(StockService.search_stocks_by_name(name))
        if code:
            code_stocks = StockService.search_stocks_by_code(code)
            # 중복 제거
            existing_ids = {stock.id for stock in stocks}
            stocks.extend([stock for stock in code_stocks if stock.id not in existing_ids])
        
        return jsonify([stock.to_dict() for stock in stocks]), 200
        
    except Exception as e:
        logger.error(f"주식 검색 실패 (name: {name}, code: {code}): {str(e)}")
        return jsonify({
            'error': '주식을 검색하는데 실패했습니다.',
            'message': str(e)
        }), 500


@stock_bp.route('/<int:stock_id>/accum', methods=['PUT'])
def update_accum_values(stock_id):
    """
    누적 초기값 업데이트
    
    Args:
        stock_id (int): 주식 ID
        
    Request Body:
        institution_accum_init (int): 기관 누적 초기값 (필수, 0 이상)
        foreigner_accum_init (int): 외국인 누적 초기값 (필수, 0 이상)
        
    Returns:
        JSON: 업데이트된 주식 정보
        
    Example:
        PUT /stocks/1/accum
        Body: {"institution_accum_init": 1500, "foreigner_accum_init": 2500}
        Response: {"id": 1, "stock_code": "005930", "stock_name": "삼성전자", "init_date": "2024-01-01", "institution_accum_init": 1500, "foreigner_accum_init": 2500}
    """
    try:
        # 입력값 검증
        if stock_id <= 0:
            return jsonify({
                'error': '유효하지 않은 주식 ID입니다.',
                'stock_id': stock_id
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
        institution_accum_init = data.get('institution_accum_init')
        if institution_accum_init is None or not isinstance(institution_accum_init, int):
            return jsonify({
                'error': '기관 누적 초기값은 필수이며 정수여야 합니다.',
                'field': 'institution_accum_init',
                'constraints': '0 이상의 정수'
            }), 400
        
        foreigner_accum_init = data.get('foreigner_accum_init')
        if foreigner_accum_init is None or not isinstance(foreigner_accum_init, int):
            return jsonify({
                'error': '외국인 누적 초기값은 필수이며 정수여야 합니다.',
                'field': 'foreigner_accum_init',
                'constraints': '0 이상의 정수'
            }), 400
        
        # 누적값 업데이트
        stock = StockService.update_accum_values(
            stock_id=stock_id,
            institution_accum_init=institution_accum_init,
            foreigner_accum_init=foreigner_accum_init
        )
        
        if not stock:
            return jsonify({
                'error': '주식을 찾을 수 없습니다.',
                'stock_id': stock_id
            }), 404
        
        logger.info(f"누적값 업데이트됨: {stock.stock_code} - {stock.stock_name} (ID: {stock.id})")
        return jsonify(stock.to_dict()), 200
        
    except ValueError as e:
        logger.warning(f"누적값 업데이트 입력값 오류 (ID: {stock_id}): {str(e)}")
        return jsonify({
            'error': str(e),
            'type': 'validation_error'
        }), 400
        
    except Exception as e:
        logger.error(f"누적값 업데이트 실패 (ID: {stock_id}): {str(e)}")
        return jsonify({
            'error': '누적값을 업데이트하는데 실패했습니다.',
            'message': str(e)
        }), 500


# 에러 핸들러
@stock_bp.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        'error': '요청한 리소스를 찾을 수 없습니다.',
        'status_code': 404
    }), 404


@stock_bp.errorhandler(405)
def method_not_allowed(error):
    """405 에러 핸들러"""
    return jsonify({
        'error': '허용되지 않은 HTTP 메서드입니다.',
        'status_code': 405
    }), 405


@stock_bp.errorhandler(500)
def internal_server_error(error):
    """500 에러 핸들러"""
    logger.error(f"내부 서버 오류: {str(error)}")
    return jsonify({
        'error': '내부 서버 오류가 발생했습니다.',
        'status_code': 500
    }), 500 