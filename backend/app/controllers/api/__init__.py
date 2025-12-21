"""
API控制器包初始化
"""
from flask import Blueprint
from app.controllers.api.query_controller import query_bp

# 创建主API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 注册子蓝图
api_bp.register_blueprint(query_bp, url_prefix='/query')

# 也可以在这里添加其他API蓝图
# api_bp.register_blueprint(another_bp, url_prefix='/another')