# -*- coding: utf-8 -*-
from flask import Flask
from flask_cors import CORS
from backend.extensions import db, cors, executor

def create_app():
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    
    # 설정 로드
    app.config.from_object('backend.config.Config')
    
    # 확장 초기화
    db.init_app(app)
    cors.init_app(app)
    executor.init_app(app)
    
    # 블루프린트 등록
    from backend.views.user import user_bp
    from backend.views.sample import sample_bp
    from backend.views.stock import stock_bp
    from backend.views.trading import trading_bp
    from backend.views.data_collector import collector_bp
    from backend.views.api_test import api_test_bp
    from backend.views.history import history_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(sample_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(collector_bp)
    app.register_blueprint(api_test_bp)
    app.register_blueprint(history_bp)
    
    # 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5001, debug=True) 