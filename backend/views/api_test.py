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
    return "http://127.0.0.1:5001"

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
        {'name': 'Sample 검색', 'method': 'GET', 'url': f'{base_url}/samples/search?name=test', 'expected_status': 200},
        
        # Stock API  
        {'name': 'Stock 목록 조회', 'method': 'GET', 'url': f'{base_url}/stocks/', 'expected_status': 200},
        {'name': 'Stock 검색', 'method': 'GET', 'url': f'{base_url}/stocks/search?name=삼성', 'expected_status': 200},
        {'name': 'Stock 코드별 조회', 'method': 'GET', 'url': f'{base_url}/stocks/code/005930', 'expected_status': 200},  # 실제 데이터가 있으므로 200이 정상
        
        # Trading API
        {'name': 'Trading 목록 조회', 'method': 'GET', 'url': f'{base_url}/trading/', 'expected_status': 200},
        {'name': 'Trading 검색', 'method': 'GET', 'url': f'{base_url}/trading/search?query=삼성', 'expected_status': 200},
        {'name': 'Trading 날짜 범위 조회', 'method': 'GET', 'url': f'{base_url}/trading/date-range?start_date=2024-01-01&end_date=2024-12-31', 'expected_status': 200},
        {'name': 'Trading 주식별 조회', 'method': 'GET', 'url': f'{base_url}/trading/stock/005930', 'expected_status': 200},
        
        # Collector API
        {'name': 'Collector 상태 조회', 'method': 'GET', 'url': f'{base_url}/collector/status', 'expected_status': 200},
        {'name': 'Collector 사용 가능한 주식 목록', 'method': 'GET', 'url': f'{base_url}/collector/stocks', 'expected_status': 200},
        {'name': 'Collector 시작', 'method': 'POST', 'url': f'{base_url}/collector/start', 'expected_status': 200, 'data': {}},
        {'name': 'Collector 중지', 'method': 'POST', 'url': f'{base_url}/collector/stop', 'expected_status': 400},  # 실행 중이 아닐 때 중지 요청 시 400은 정상
        {'name': 'Collector 리셋', 'method': 'POST', 'url': f'{base_url}/collector/reset', 'expected_status': 200},
        {'name': 'Collector 누적 계산', 'method': 'POST', 'url': f'{base_url}/collector/calculate-accumulated', 'expected_status': 200},
        
        # User API
        {'name': 'User 목록 조회', 'method': 'GET', 'url': f'{base_url}/users/', 'expected_status': 200},
        
        # API Test
        {'name': 'Health Check', 'method': 'GET', 'url': f'{base_url}/api-test/health', 'expected_status': 200},
        {'name': 'Database 테스트', 'method': 'GET', 'url': f'{base_url}/api-test/database', 'expected_status': 200},
    ]
    
    for endpoint in endpoints:
        try:
            # HTTP 요청 실행
            headers = {'Content-Type': 'application/json'}
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=5)
            elif endpoint['method'] == 'POST':
                data = endpoint.get('data', {})
                response = requests.post(endpoint['url'], json=data, headers=headers, timeout=5)
            elif endpoint['method'] == 'PUT':
                data = endpoint.get('data', {})
                response = requests.put(endpoint['url'], json=data, headers=headers, timeout=5)
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
    데이터베이스 테이블 초기화 (기존 데이터 보존)
    """
    try:
        from backend.extensions import db
        from backend.models.stock import StockList
        from backend.models.sample import Sample
        from backend.models.trading import StockInvestorTrading
        from backend.models.user import User
        
        # 테이블 생성
        db.create_all()
        
        # 테이블 개수 확인
        total_tables = 4  # stock_list, tb_sample, stock_investor_trading, user
        
        return jsonify({
            'status': 'success',
            'message': f'데이터베이스 테이블이 생성되었습니다. ({total_tables}개 테이블)',
            'total_tables': total_tables,
            'timestamp': datetime.now().isoformat()
        }), 200
        
        except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'데이터베이스 초기화 실패: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@api_test_bp.route('/database/reset', methods=['POST'])
def reset_database():
    """
    테스트 데이터 초기화 (모든 데이터 삭제)
    """
    try:
        from backend.extensions import db
        from backend.models.stock import StockList
        from backend.models.sample import Sample
        from backend.models.trading import StockInvestorTrading
        from backend.models.user import User
        
        # 모든 데이터 삭제
        StockInvestorTrading.query.delete()
        StockList.query.delete()
        Sample.query.delete()
        User.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '모든 테스트 데이터가 초기화되었습니다.',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"데이터베이스 초기화 실패: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'데이터베이스 초기화 실패: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500 