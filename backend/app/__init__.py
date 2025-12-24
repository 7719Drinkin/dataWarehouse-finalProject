from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name='development'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化扩展
    CORS(app)  # 允许跨域请求

    # 注册蓝图
    from app.controllers.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 注册错误处理器
    register_error_handlers(app)

    # 注册请求处理器
    register_request_handlers(app)

    return app

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'success': False}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error', 'success': False}, 500

    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'success': False}, 400

def register_request_handlers(app):
    """注册请求处理器"""
    @app.before_request
    def before_request():
        # 可以在这里添加请求日志等
        pass

    @app.after_request
    def after_request(response):
        # 可以在这里添加响应头等
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

