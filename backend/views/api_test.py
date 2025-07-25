"""
API 테스트 관련 Blueprint
서버 기동 시 REST API의 상태를 테스트하는 기능을 제공합니다.
"""
from flask import Blueprint, jsonify
import requests
import logging
from datetime import datetime

# Blueprint 생성
api_test_bp = Blueprint('api_test', __name__, url_prefix='/api-test')

# 로거 설정
logger = logging.getLogger(__name__)

def get_base_url():
    """기본 URL 반환"""
    return "http://127.0.0.1:5000"

@api_test_bp.route('/health', methods=['GET'])
def health_check():
    """
    서버 상태 확인
    """
    try:
        return jsonify({
            'status': 'healthy',
            'message': 'API 서버가 정상적으로 작동 중입니다.',
            'timestamp': datetime.now().isoformat(),
            'server': 'Flask Development Server'
        }), 200
    except Exception as e:
        logger.error(f"Health check 실패: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'서버 상태 확인 실패: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_test_bp.route('/endpoints', methods=['GET'])
def test_all_endpoints():
    """
    모든 주요 API 엔드포인트 테스트
    """
    base_url = get_base_url()
    test_results = []
    
    # 테스트할 엔드포인트 목록
    endpoints = [
        # Sample API
        {'name': 'Sample 목록 조회', 'method': 'GET', 'url': f'{base_url}/samples/', 'expected_status': 200},
        
        # Stock API  
        {'name': 'Stock 목록 조회', 'method': 'GET', 'url': f'{base_url}/stocks/', 'expected_status': 200},
        
        # Trading API
        {'name': 'Trading 목록 조회', 'method': 'GET', 'url': f'{base_url}/trading/', 'expected_status': 200},
        
        # Collector API
        {'name': 'Collector 상태 조회', 'method': 'GET', 'url': f'{base_url}/collector/status', 'expected_status': 200},
        {'name': 'Collector 사용 가능한 주식 목록', 'method': 'GET', 'url': f'{base_url}/collector/stocks', 'expected_status': 200},
        
        # User API
        {'name': 'User 목록 조회', 'method': 'GET', 'url': f'{base_url}/users/', 'expected_status': 200},
        
        # API Test
        {'name': 'Health Check', 'method': 'GET', 'url': f'{base_url}/api-test/health', 'expected_status': 200},
    ]
    
    for endpoint in endpoints:
        try:
            # HTTP 요청 실행
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=5)
            elif endpoint['method'] == 'POST':
                response = requests.post(endpoint['url'], timeout=5)
            elif endpoint['method'] == 'PUT':
                response = requests.put(endpoint['url'], timeout=5)
            elif endpoint['method'] == 'DELETE':
                response = requests.delete(endpoint['url'], timeout=5)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {endpoint['method']}")
            
            # 결과 분석
            is_success = response.status_code == endpoint['expected_status']
            
            test_result = {
                'name': endpoint['name'],
                'method': endpoint['method'],
                'url': endpoint['url'],
                'expected_status': endpoint['expected_status'],
                'actual_status': response.status_code,
                'success': is_success,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'timestamp': datetime.now().isoformat()
            }
            
            # 응답 데이터 추가 (크기 제한)
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_data = response.json()
                    # 응답 데이터가 너무 크면 요약
                    if isinstance(response_data, list) and len(response_data) > 3:
                        test_result['response_preview'] = {
                            'type': 'array',
                            'length': len(response_data),
                            'sample': response_data[:2] if response_data else []
                        }
                    elif isinstance(response_data, dict):
                        test_result['response_preview'] = response_data
                    else:
                        test_result['response_preview'] = response_data
                else:
                    test_result['response_preview'] = response.text[:200] + '...' if len(response.text) > 200 else response.text
            except Exception as e:
                test_result['response_preview'] = f'응답 파싱 실패: {str(e)}'
            
        except requests.exceptions.Timeout:
            test_result = {
                'name': endpoint['name'],
                'method': endpoint['method'], 
                'url': endpoint['url'],
                'expected_status': endpoint['expected_status'],
                'actual_status': None,
                'success': False,
                'error': '요청 타임아웃 (5초)',
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            test_result = {
                'name': endpoint['name'],
                'method': endpoint['method'],
                'url': endpoint['url'], 
                'expected_status': endpoint['expected_status'],
                'actual_status': None,
                'success': False,
                'error': '연결 실패 (서버가 실행되지 않음)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            test_result = {
                'name': endpoint['name'],
                'method': endpoint['method'],
                'url': endpoint['url'],
                'expected_status': endpoint['expected_status'],
                'actual_status': None,
                'success': False,
                'error': f'예외 발생: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        
        test_results.append(test_result)
        logger.info(f"API 테스트 완료: {endpoint['name']} - {'성공' if test_result['success'] else '실패'}")
    
    # 전체 결과 요약
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results if result['success'])
    failed_tests = total_tests - successful_tests
    
    summary = {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'failed_tests': failed_tests,
        'success_rate': round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
        'test_timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'summary': summary,
        'results': test_results
    }), 200

@api_test_bp.route('/endpoint/<path:endpoint_path>', methods=['GET'])
def test_single_endpoint(endpoint_path):
    """
    특정 엔드포인트 단일 테스트
    """
    base_url = get_base_url()
    full_url = f"{base_url}/{endpoint_path}"
    
    try:
        response = requests.get(full_url, timeout=5)
        
        result = {
            'url': full_url,
            'status_code': response.status_code,
            'success': 200 <= response.status_code < 300,
            'response_time_ms': response.elapsed.total_seconds() * 1000,
            'headers': dict(response.headers),
            'timestamp': datetime.now().isoformat()
        }
        
        # 응답 데이터 추가
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                result['response_data'] = response.json()
            else:
                result['response_data'] = response.text
        except Exception as e:
            result['response_data'] = f'응답 파싱 실패: {str(e)}'
        
        return jsonify(result), 200
        
    except requests.exceptions.Timeout:
        return jsonify({
            'url': full_url,
            'success': False,
            'error': '요청 타임아웃 (5초)',
            'timestamp': datetime.now().isoformat()
        }), 408
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'url': full_url,
            'success': False,
            'error': '연결 실패',
            'timestamp': datetime.now().isoformat()
        }), 503
        
    except Exception as e:
        return jsonify({
            'url': full_url,
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_test_bp.route('/database', methods=['GET'])
def test_database_connection():
    """
    데이터베이스 연결 상태 테스트
    """
    try:
        from backend.extensions import db
        from backend.models.sample import Sample
        from backend.models.stock import StockList
        from backend.models.trading import StockInvestorTrading
        
        tables_status = {}
        
        # 각 테이블의 레코드 수 확인
        try:
            sample_count = Sample.query.count()
            tables_status['tb_sample'] = {
                'status': 'accessible',
                'record_count': sample_count
            }
        except Exception as e:
            tables_status['tb_sample'] = {
                'status': 'error',
                'error': str(e),
                'record_count': 0
            }
        
        try:
            stock_count = StockList.query.count()
            tables_status['stock_list'] = {
                'status': 'accessible', 
                'record_count': stock_count
            }
        except Exception as e:
            tables_status['stock_list'] = {
                'status': 'error',
                'error': str(e),
                'record_count': 0
            }
        
        try:
            trading_count = StockInvestorTrading.query.count()
            tables_status['stock_investor_trading'] = {
                'status': 'accessible',
                'record_count': trading_count
            }
        except Exception as e:
            tables_status['stock_investor_trading'] = {
                'status': 'error',
                'error': str(e),
                'record_count': 0
            }
        
        # 전체 상태 결정
        has_errors = any(table.get('status') == 'error' for table in tables_status.values())
        
        return jsonify({
            'database_status': 'connected_with_errors' if has_errors else 'connected',
            'tables': tables_status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"데이터베이스 테스트 실패: {str(e)}")
        return jsonify({
            'database_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_test_bp.route('/database/init', methods=['POST'])
def initialize_database():
    """
    데이터베이스 테이블 생성 (기존 데이터 보존)
    SQLAlchemy의 create_all()을 사용하여 테이블이 없는 경우에만 생성
    """
    try:
        from backend.extensions import db
        from backend.models.sample import Sample
        from backend.models.stock import StockList
        from backend.models.trading import StockInvestorTrading
        from backend.models.user import User
        
        # 모든 테이블 생성
        db.create_all()
        
        # 생성된 테이블 확인
        tables_created = []
        
        # 각 모델이 정상적으로 접근 가능한지 확인
        try:
            Sample.query.count()
            tables_created.append('tb_sample')
        except Exception as e:
            logger.warning(f"tb_sample 테이블 확인 실패: {str(e)}")
        
        try:
            StockList.query.count()
            tables_created.append('stock_list')
        except Exception as e:
            logger.warning(f"stock_list 테이블 확인 실패: {str(e)}")
        
        try:
            StockInvestorTrading.query.count()
            tables_created.append('stock_investor_trading')
        except Exception as e:
            logger.warning(f"stock_investor_trading 테이블 확인 실패: {str(e)}")
        
        try:
            User.query.count()
            tables_created.append('users')
        except Exception as e:
            logger.warning(f"users 테이블 확인 실패: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': '데이터베이스 테이블이 성공적으로 생성되었습니다. (기존 데이터는 보존됨)',
            'tables_created': tables_created,
            'total_tables': len(tables_created),
            'note': 'create_all()은 테이블이 없는 경우에만 생성하며, 기존 데이터를 삭제하지 않습니다.',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"데이터베이스 테이블 생성 실패: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'데이터베이스 테이블 생성 실패: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500 