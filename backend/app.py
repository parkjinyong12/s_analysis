from flask import Flask
from backend.extensions import db, cors
import os

def create_app():
    app = Flask(__name__)
    cors.init_app(app)
    app.config.from_object('backend.config.Config')
    db.init_app(app)
    
    # Blueprint 등록
    from backend.views.user import user_bp
    app.register_blueprint(user_bp)
    
    from backend.views.sample import sample_bp
    app.register_blueprint(sample_bp)
    
    from backend.views.stock import stock_bp
    app.register_blueprint(stock_bp)
    
    from backend.views.trading import trading_bp
    app.register_blueprint(trading_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True) 