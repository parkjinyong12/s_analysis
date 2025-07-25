"""
Data Collector REST API 뷰
데이터 수집 작업을 관리하는 API 엔드포인트를 제공합니다.
"""
from flask import Blueprint, jsonify, request
from backend.services.data_collector import DataCollectorService
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

# 로거 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
collector_bp = Blueprint('collector', __name__, url_prefix='/collector')

# 전역 상태 관리
collection_status = {
    'is_running': False,
    'current_stock': '',
    'progress': 0,
    'total_stocks': 0,
    'success_count': 0,
    'failed_count': 0,
    'start_time': None,
    'end_time': None,
    'current_phase': 'idle',  # idle, initializing, collecting, completed, error
    'error_message': '',
    'failed_stocks': []
}


def reset_collection_status():
    """수집 상태 초기화"""
    global collection_status
    collection_status.update({
        'is_running': False,
        'current_stock': '',
        'progress': 0,
        'total_stocks': 0,
        'success_count': 0,
        'failed_count': 0,
        'start_time': None,
        'end_time': None,
        'current_phase': 'idle',
        'error_message': '',
        'failed_stocks': []
    })


def update_progress(phase: str, current_stock: str = '', progress: int = 0, 
                   success_count: int = 0, failed_count: int = 0, 
                   error_message: str = '', failed_stock: str = ''):
    """진행률 업데이트"""
    global collection_status
    
    collection_status.update({
        'current_phase': phase,
        'current_stock': current_stock,
        'progress': progress,
        'success_count': success_count,
        'failed_count': failed_count,
        'error_message': error_message
    })
    
    if failed_stock and failed_stock not in collection_status['failed_stocks']:
        collection_status['failed_stocks'].append(failed_stock)
    
    logger.info(f"진행률 업데이트: {phase} - {current_stock} ({progress}%)")


def collect_data_background(years: int = 3):
    """백그라운드에서 데이터 수집 실행"""
    global collection_status
    
    try:
        collection_status['is_running'] = True
        collection_status['start_time'] = datetime.now().isoformat()
        
        logger.info("백그라운드 데이터 수집 시작")
        
        # 1. 초기화 단계
        update_progress('initializing', '주식 목록 초기화 중...', 0)
        
        # 주식 목록 초기화
        if not DataCollectorService.initialize_stock_list():
            update_progress('error', '', 0, 0, 0, '주식 목록 초기화 실패')
            return
        
        # 2. 주식 목록 조회
        from backend.services.stock_service import StockService
        stocks = StockService.get_all_stocks()
        collection_status['total_stocks'] = len(stocks)
        
        if not stocks:
            update_progress('error', '', 0, 0, 0, '수집할 주식이 없습니다')
            return
        
        logger.info(f"총 {len(stocks)}개 주식 데이터 수집 시작")
        
        # 3. 데이터 수집 단계
        update_progress('collecting', '', 0, 0, 0)
        
        success_count = 0
        failed_count = 0
        
        for i, stock in enumerate(stocks):
            if not collection_status['is_running']:  # 중단 요청 확인
                logger.info("데이터 수집이 사용자에 의해 중단되었습니다")
                break
            
            try:
                # 현재 진행률 계산
                progress = int((i / len(stocks)) * 100)
                update_progress('collecting', f"{stock.stock_code} {stock.stock_name}", 
                              progress, success_count, failed_count)
                
                # 데이터 수집 실행
                success = DataCollectorService.collect_and_save_trading_data(
                    stock.stock_code, stock.stock_name, years
                )
                
                if success:
                    success_count += 1
                    logger.info(f"수집 완료: {stock.stock_code} {stock.stock_name}")
                else:
                    failed_count += 1
                    update_progress('collecting', f"{stock.stock_code} {stock.stock_name}", 
                                  progress, success_count, failed_count, 
                                  '', f"{stock.stock_code} {stock.stock_name}")
                    logger.warning(f"수집 실패: {stock.stock_code} {stock.stock_name}")
                
                # 요청 간 대기
                time.sleep(DataCollectorService.REQUEST_DELAY)
                
            except Exception as e:
                failed_count += 1
                error_msg = f"{stock.stock_code} {stock.stock_name}: {str(e)}"
                update_progress('collecting', f"{stock.stock_code} {stock.stock_name}", 
                              progress, success_count, failed_count, 
                              '', error_msg)
                logger.error(f"주식 데이터 수집 중 오류: {error_msg}")
                continue
        
        # 4. 완료 단계
        final_progress = 100
        collection_status['end_time'] = datetime.now().isoformat()
        
        if collection_status['is_running']:  # 정상 완료
            update_progress('completed', '데이터 수집 완료', final_progress, 
                          success_count, failed_count)
            logger.info(f"데이터 수집 완료: 성공 {success_count}개, 실패 {failed_count}개")
        else:  # 중단됨
            update_progress('cancelled', '데이터 수집 중단됨', progress, 
                          success_count, failed_count)
            logger.info("데이터 수집이 중단되었습니다")
        
    except Exception as e:
        collection_status['end_time'] = datetime.now().isoformat()
        update_progress('error', '', 0, 0, 0, f'데이터 수집 중 오류: {str(e)}')
        logger.error(f"데이터 수집 중 치명적 오류: {e}")
    
    finally:
        collection_status['is_running'] = False


@collector_bp.route('/status', methods=['GET'])
def get_collection_status():
    """
    데이터 수집 상태 조회
    
    Returns:
        JSON: 현재 수집 상태 정보
        
    Example:
        GET /collector/status
        Response: {
            "is_running": true,
            "current_stock": "005930 삼성전자",
            "progress": 45,
            "total_stocks": 50,
            "success_count": 20,
            "failed_count": 2,
            "current_phase": "collecting",
            "start_time": "2024-01-01T10:00:00",
            "failed_stocks": ["000001 주식A"]
        }
    """
    try:
        # 경과 시간 계산
        elapsed_time = None
        if collection_status['start_time']:
            start_time = datetime.fromisoformat(collection_status['start_time'])
            if collection_status['end_time']:
                end_time = datetime.fromisoformat(collection_status['end_time'])
                elapsed_time = str(end_time - start_time)
            else:
                elapsed_time = str(datetime.now() - start_time)
        
        response_data = {
            **collection_status,
            'elapsed_time': elapsed_time
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"상태 조회 실패: {str(e)}")
        return jsonify({
            'error': '상태 조회에 실패했습니다.',
            'message': str(e)
        }), 500


@collector_bp.route('/start', methods=['POST'])
def start_collection():
    """
    데이터 수집 시작
    
    Request Body:
        years (int): 수집할 기간 (년 단위, 선택, 기본값: 3)
        
    Returns:
        JSON: 수집 시작 결과
        
    Example:
        POST /collector/start
        Body: {"years": 3}
        Response: {"result": "success", "message": "데이터 수집이 시작되었습니다."}
    """
    try:
        # 이미 실행 중인지 확인
        if collection_status['is_running']:
            return jsonify({
                'error': '데이터 수집이 이미 실행 중입니다.',
                'current_phase': collection_status['current_phase']
            }), 400
        
        # 요청 데이터 파싱
        data = request.get_json() if request.is_json else {}
        years = data.get('years', 3)
        
        # 입력값 검증
        if not isinstance(years, int) or years < 1 or years > 10:
            return jsonify({
                'error': '수집 기간은 1년 이상 10년 이하의 정수여야 합니다.',
                'field': 'years'
            }), 400
        
        # 상태 초기화
        reset_collection_status()
        
        # 백그라운드 스레드에서 데이터 수집 시작
        collection_thread = threading.Thread(
            target=collect_data_background, 
            args=(years,),
            daemon=True
        )
        collection_thread.start()
        
        logger.info(f"데이터 수집 시작 요청: {years}년")
        
        return jsonify({
            'result': 'success',
            'message': f'{years}년간의 데이터 수집이 시작되었습니다.',
            'years': years
        }), 200
        
    except Exception as e:
        logger.error(f"데이터 수집 시작 실패: {str(e)}")
        return jsonify({
            'error': '데이터 수집을 시작하는데 실패했습니다.',
            'message': str(e)
        }), 500


@collector_bp.route('/stop', methods=['POST'])
def stop_collection():
    """
    데이터 수집 중단
    
    Returns:
        JSON: 수집 중단 결과
        
    Example:
        POST /collector/stop
        Response: {"result": "success", "message": "데이터 수집 중단 요청이 전송되었습니다."}
    """
    try:
        if not collection_status['is_running']:
            return jsonify({
                'error': '실행 중인 데이터 수집이 없습니다.',
                'current_phase': collection_status['current_phase']
            }), 400
        
        # 중단 플래그 설정
        collection_status['is_running'] = False
        collection_status['current_phase'] = 'stopping'
        
        logger.info("데이터 수집 중단 요청")
        
        return jsonify({
            'result': 'success',
            'message': '데이터 수집 중단 요청이 전송되었습니다.'
        }), 200
        
    except Exception as e:
        logger.error(f"데이터 수집 중단 실패: {str(e)}")
        return jsonify({
            'error': '데이터 수집을 중단하는데 실패했습니다.',
            'message': str(e)
        }), 500


@collector_bp.route('/reset', methods=['POST'])
def reset_collection():
    """
    데이터 수집 상태 초기화
    
    Returns:
        JSON: 초기화 결과
        
    Example:
        POST /collector/reset
        Response: {"result": "success", "message": "수집 상태가 초기화되었습니다."}
    """
    try:
        if collection_status['is_running']:
            return jsonify({
                'error': '실행 중인 데이터 수집이 있습니다. 먼저 중단해주세요.',
                'current_phase': collection_status['current_phase']
            }), 400
        
        reset_collection_status()
        
        logger.info("데이터 수집 상태 초기화")
        
        return jsonify({
            'result': 'success',
            'message': '수집 상태가 초기화되었습니다.'
        }), 200
        
    except Exception as e:
        logger.error(f"상태 초기화 실패: {str(e)}")
        return jsonify({
            'error': '상태를 초기화하는데 실패했습니다.',
            'message': str(e)
        }), 500


@collector_bp.route('/stocks', methods=['GET'])
def get_available_stocks():
    """
    수집 가능한 주식 목록 조회
    
    Returns:
        JSON: 주식 목록
        
    Example:
        GET /collector/stocks
        Response: [{"code": "005930", "name": "삼성전자"}, ...]
    """
    try:
        # 기본 제공 주식 목록 반환
        stocks = [
            {"code": stock["code"], "name": stock["name"]} 
            for stock in DataCollectorService.DEFAULT_STOCK_LIST
        ]
        
        return jsonify({
            'stocks': stocks,
            'total_count': len(stocks)
        }), 200
        
    except Exception as e:
        logger.error(f"주식 목록 조회 실패: {str(e)}")
        return jsonify({
            'error': '주식 목록을 조회하는데 실패했습니다.',
            'message': str(e)
        }), 500


# 에러 핸들러
@collector_bp.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        'error': '요청한 리소스를 찾을 수 없습니다.',
        'status_code': 404
    }), 404


@collector_bp.errorhandler(405)
def method_not_allowed(error):
    """405 에러 핸들러"""
    return jsonify({
        'error': '허용되지 않은 HTTP 메서드입니다.',
        'status_code': 405
    }), 405


@collector_bp.errorhandler(500)
def internal_server_error(error):
    """500 에러 핸들러"""
    logger.error(f"내부 서버 오류: {str(error)}")
    return jsonify({
        'error': '내부 서버 오류가 발생했습니다.',
        'status_code': 500
    }), 500 