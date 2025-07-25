"""
주식 데이터 수집 서비스
네이버 금융에서 주식 거래 데이터를 크롤링하여 DB에 저장하는 서비스
"""
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from backend.services.stock_service import StockService
from backend.services.trading_service import TradingService
import logging

# 로거 설정
logger = logging.getLogger(__name__)


class DataCollectorService:
    """주식 데이터 수집 서비스 클래스"""
    
    # 기본 설정
    BASE_URL = "https://finance.naver.com/item/frgn.naver"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    REQUEST_DELAY = 0.5  # 요청 간 대기 시간 (초)
    
    # 대형주 종목 리스트 (시가총액 상위 50개)
    DEFAULT_STOCK_LIST = [
        {"code": "005930", "name": "삼성전자"},
        {"code": "000660", "name": "SK하이닉스"},
        {"code": "207940", "name": "삼성바이오로직스"},
        {"code": "373220", "name": "LG에너지솔루션"},
        {"code": "005380", "name": "현대차"},
        {"code": "068270", "name": "셀트리온"},
        {"code": "000270", "name": "기아"},
        {"code": "035420", "name": "NAVER"},
        {"code": "105560", "name": "KB금융"},
        {"code": "012450", "name": "한화에어로스페이스"},
        {"code": "005490", "name": "POSCO홀딩스"},
        {"code": "329180", "name": "HD현대중공업"},
        {"code": "012330", "name": "현대모비스"},
        {"code": "055550", "name": "신한지주"},
        {"code": "042660", "name": "한화오션"},
        {"code": "138040", "name": "메리츠금융지주"},
        {"code": "028260", "name": "삼성물산"},
        {"code": "035720", "name": "카카오"},
        {"code": "096770", "name": "SK이노베이션"},
        {"code": "000810", "name": "삼성화재"},
        {"code": "051910", "name": "LG화학"},
        {"code": "086790", "name": "하나금융지주"},
        {"code": "010130", "name": "고려아연"},
        {"code": "011200", "name": "HMM"},
        {"code": "034020", "name": "두산에너빌리티"},
        {"code": "032830", "name": "삼성생명"},
        {"code": "259960", "name": "크래프톤"},
        {"code": "009540", "name": "HD한국조선해양"},
        {"code": "015760", "name": "한국전력"},
        {"code": "006400", "name": "삼성SDI"},
        {"code": "066570", "name": "LG전자"},
        {"code": "402340", "name": "SK스퀘어"},
        {"code": "010140", "name": "삼성중공업"},
        {"code": "030200", "name": "KT"},
        {"code": "024110", "name": "기업은행"},
        {"code": "316140", "name": "우리금융지주"},
        {"code": "033780", "name": "KT&G"},
        {"code": "004990", "name": "롯데지주"},
        {"code": "017670", "name": "SK텔레콤"},
        {"code": "267260", "name": "HD현대일렉트릭"},
        {"code": "003550", "name": "LG"},
        {"code": "323410", "name": "카카오뱅크"},
        {"code": "003670", "name": "포스코퓨처엠"},
        {"code": "047050", "name": "포스코인터내셔널"},
        {"code": "009150", "name": "삼성전기"},
        {"code": "034730", "name": "SK"},
        {"code": "000100", "name": "유한양행"},
        {"code": "352820", "name": "하이브"},
        {"code": "018260", "name": "삼성에스디에스"},
        {"code": "086280", "name": "현대글로비스"}
    ]
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[str]:
        """
        날짜 문자열을 파싱하여 YYYY-MM-DD 형식으로 변환
        
        Args:
            date_str (str): 원본 날짜 문자열 (YYYY.MM.DD 형식)
            
        Returns:
            Optional[str]: 변환된 날짜 문자열 (YYYY-MM-DD) 또는 None
        """
        try:
            date_obj = datetime.strptime(date_str.strip(), "%Y.%m.%d")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError as e:
            logger.warning(f"날짜 파싱 오류: {e}, date_str: {date_str}")
            return None
    
    @staticmethod
    def parse_number(number_str: str) -> Optional[int]:
        """
        숫자 문자열을 파싱하여 정수로 변환
        
        Args:
            number_str (str): 원본 숫자 문자열 (콤마, +/- 기호 포함)
            
        Returns:
            Optional[int]: 변환된 정수 또는 None
        """
        try:
            # 콤마와 + 기호 제거, - 기호는 유지
            cleaned = number_str.strip().replace(',', '').replace('+', '')
            return int(cleaned) if cleaned and cleaned != '-' else 0
        except (ValueError, AttributeError) as e:
            logger.warning(f"숫자 파싱 오류: {e}, number_str: {number_str}")
            return None
    
    @staticmethod
    def crawl_trading_data(stock_code: str, years: int = 3) -> List[Dict]:
        """
        네이버 금융에서 특정 주식의 거래 데이터를 크롤링
        
        Args:
            stock_code (str): 주식 코드 (6자리)
            years (int): 수집할 기간 (년 단위, 기본값: 3년)
            
        Returns:
            List[Dict]: 거래 데이터 리스트
        """
        logger.info(f"주식 데이터 크롤링 시작: {stock_code} ({years}년)")
        
        # 날짜 범위 설정
        end_date = datetime.today()
        start_date = end_date - timedelta(days=years * 365)
        
        data = []
        page = 1
        
        while True:
            try:
                # URL 구성 및 요청
                url = f"{DataCollectorService.BASE_URL}?code={stock_code}&page={page}"
                response = requests.get(url, headers=DataCollectorService.HEADERS, timeout=10)
                
                if response.status_code != 200:
                    logger.error(f"페이지 로딩 실패 (페이지 {page}): HTTP {response.status_code}")
                    break
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, "html.parser")
                tables = soup.select("table.type2")
                
                if not tables or len(tables) < 2:
                    logger.warning(f"테이블을 찾을 수 없습니다 (페이지 {page})")
                    break
                
                # 두 번째 테이블에서 데이터 추출
                table = tables[1]
                rows = table.select("tr")
                
                page_has_data = False
                
                for row in rows[2:]:  # 헤더 행 제외
                    cols = row.find_all("td")
                    if len(cols) <= 6:  # 필요한 컬럼 수 확인
                        continue
                    
                    # 날짜 파싱
                    date_str = cols[0].text.strip()
                    if not date_str:
                        continue
                    
                    parsed_date = DataCollectorService.parse_date(date_str)
                    if not parsed_date:
                        continue
                    
                    date_obj = datetime.strptime(parsed_date, "%Y-%m-%d")
                    
                    # 날짜 범위 체크
                    if date_obj < start_date:
                        logger.info(f"수집 기간 종료: {parsed_date}")
                        return data
                    
                    # 데이터 파싱
                    close_price = DataCollectorService.parse_number(cols[1].text)
                    institution_net_buy = DataCollectorService.parse_number(cols[5].text)
                    foreigner_net_buy = DataCollectorService.parse_number(cols[6].text)
                    
                    # 파싱된 데이터 검증
                    if any(x is None for x in [close_price, institution_net_buy, foreigner_net_buy]):
                        logger.warning(f"데이터 파싱 실패: {date_str}")
                        continue
                    
                    page_has_data = True
                    data.append({
                        'trade_date': parsed_date,
                        'close_price': close_price,
                        'institution_net_buy': institution_net_buy,
                        'foreigner_net_buy': foreigner_net_buy
                    })
                
                if not page_has_data:
                    logger.info(f"더 이상 데이터가 없습니다 (페이지 {page})")
                    break
                
                page += 1
                time.sleep(DataCollectorService.REQUEST_DELAY)  # 서버 부하 방지
                
            except requests.RequestException as e:
                logger.error(f"네트워크 오류 (페이지 {page}): {e}")
                break
            except Exception as e:
                logger.error(f"예상치 못한 오류 (페이지 {page}): {e}")
                break
        
        logger.info(f"크롤링 완료: {stock_code}, 총 {len(data)}개 데이터")
        return data
    
    @staticmethod
    def initialize_stock_list() -> bool:
        """
        기본 주식 목록을 DB에 초기화
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("주식 목록 초기화 시작")
            
            success_count = 0
            for stock_info in DataCollectorService.DEFAULT_STOCK_LIST:
                try:
                    # 이미 존재하는지 확인
                    existing_stock = StockService.get_stock_by_code(stock_info['code'])
                    if existing_stock:
                        logger.debug(f"이미 존재하는 주식: {stock_info['code']} {stock_info['name']}")
                        continue
                    
                    # 새로운 주식 추가
                    stock = StockService.create_stock(
                        stock_code=stock_info['code'],
                        stock_name=stock_info['name']
                    )
                    
                    if stock:
                        success_count += 1
                        logger.debug(f"주식 추가 완료: {stock_info['code']} {stock_info['name']}")
                    
                except Exception as e:
                    logger.error(f"주식 추가 실패: {stock_info['code']} {stock_info['name']}, 오류: {e}")
                    continue
            
            logger.info(f"주식 목록 초기화 완료: {success_count}개 추가")
            return True
            
        except Exception as e:
            logger.error(f"주식 목록 초기화 실패: {e}")
            return False
    
    @staticmethod
    def collect_and_save_trading_data(stock_code: str, stock_name: str, years: int = 3) -> bool:
        """
        특정 주식의 거래 데이터를 크롤링하여 DB에 저장
        
        Args:
            stock_code (str): 주식 코드
            stock_name (str): 주식명
            years (int): 수집할 기간 (년 단위)
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"거래 데이터 수집 시작: {stock_code} {stock_name}")
            
            # 데이터 크롤링
            trading_data = DataCollectorService.crawl_trading_data(stock_code, years)
            
            if not trading_data:
                logger.warning(f"수집된 데이터가 없습니다: {stock_code}")
                return False
            
            # DB에 저장
            success_count = 0
            for data in trading_data:
                try:
                    # 중복 데이터 체크 (같은 주식 코드 + 같은 날짜)
                    existing_data = TradingService.get_trading_data_by_stock_code(stock_code)
                    existing_dates = {d.trade_date for d in existing_data}
                    
                    if data['trade_date'] in existing_dates:
                        continue  # 이미 존재하는 데이터 스킵
                    
                    # 새로운 거래 데이터 저장
                    trading_record = TradingService.create_trading_data(
                        stock_code=stock_code,
                        stock_name=stock_name,
                        trade_date=data['trade_date'],
                        close_price=data['close_price'],
                        institution_net_buy=data['institution_net_buy'],
                        foreigner_net_buy=data['foreigner_net_buy']
                    )
                    
                    if trading_record:
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"거래 데이터 저장 실패: {stock_code} {data['trade_date']}, 오류: {e}")
                    continue
            
            logger.info(f"거래 데이터 저장 완료: {stock_code}, {success_count}개 저장")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"거래 데이터 수집 실패: {stock_code}, 오류: {e}")
            return False
    
    @staticmethod
    def collect_all_stocks_data(years: int = 3) -> Dict[str, any]:
        """
        모든 주식의 거래 데이터를 수집
        
        Args:
            years (int): 수집할 기간 (년 단위)
            
        Returns:
            Dict: 수집 결과 통계
        """
        logger.info(f"전체 주식 데이터 수집 시작 ({years}년)")
        
        results = {
            'total_stocks': 0,
            'success_stocks': 0,
            'failed_stocks': 0,
            'failed_list': []
        }
        
        try:
            # 1. 주식 목록 초기화
            DataCollectorService.initialize_stock_list()
            
            # 2. DB에서 주식 목록 조회
            stocks = StockService.get_all_stocks()
            results['total_stocks'] = len(stocks)
            
            # 3. 각 주식별 데이터 수집
            for stock in stocks:
                try:
                    logger.info(f"데이터 수집 중: {stock.stock_code} {stock.stock_name}")
                    
                    success = DataCollectorService.collect_and_save_trading_data(
                        stock.stock_code, stock.stock_name, years
                    )
                    
                    if success:
                        results['success_stocks'] += 1
                        logger.info(f"수집 완료: {stock.stock_code} {stock.stock_name}")
                    else:
                        results['failed_stocks'] += 1
                        results['failed_list'].append(f"{stock.stock_code} {stock.stock_name}")
                        logger.warning(f"수집 실패: {stock.stock_code} {stock.stock_name}")
                    
                    # 요청 간 대기
                    time.sleep(DataCollectorService.REQUEST_DELAY)
                    
                except Exception as e:
                    results['failed_stocks'] += 1
                    results['failed_list'].append(f"{stock.stock_code} {stock.stock_name}: {str(e)}")
                    logger.error(f"주식 데이터 수집 중 오류: {stock.stock_code}, {e}")
                    continue
            
            logger.info(f"전체 데이터 수집 완료: 성공 {results['success_stocks']}개, 실패 {results['failed_stocks']}개")
            return results
            
        except Exception as e:
            logger.error(f"전체 데이터 수집 중 오류: {e}")
            results['error'] = str(e)
            return results


# 독립 실행용 함수
def main():
    """메인 실행 함수"""
    import logging
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 전체 주식 데이터 수집 실행
    results = DataCollectorService.collect_all_stocks_data(years=3)
    
    print("\n" + "="*50)
    print("데이터 수집 결과")
    print("="*50)
    print(f"전체 주식 수: {results['total_stocks']}")
    print(f"성공: {results['success_stocks']}")
    print(f"실패: {results['failed_stocks']}")
    
    if results['failed_list']:
        print("\n실패 목록:")
        for failed in results['failed_list']:
            print(f"  - {failed}")
    
    print("="*50)


if __name__ == "__main__":
    main() 