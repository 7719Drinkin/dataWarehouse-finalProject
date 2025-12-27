"""API 控制器包初始化

这里定义主 API 蓝图（/api），并注册各个子蓝图：

1) 聚合查询（默认）：
- /api/query/...
- 由 query_controller.py 提供，内部使用 QueryAggregator.execute_on_all 并发查询三库。

2) 单库查询（新增）：
- /api/query/opengauss/...
- /api/query/hive/...
- /api/query/neo4j/...
- 分别由 opengauss_query_controller.py / hive_query_controller.py / neo4j_query_controller.py 提供。

这样前端就可以根据用户选择的数据库，决定调用单库接口还是聚合接口。
"""
from flask import Blueprint

from app.controllers.api.query_controller import query_bp
from app.controllers.api.opengauss_query_controller import opengauss_query_bp
from app.controllers.api.hive_query_controller import hive_query_bp
from app.controllers.api.neo4j_query_controller import neo4j_query_bp

# 创建主API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 注册子蓝图
# 聚合查询（默认：三库并发）
api_bp.register_blueprint(query_bp, url_prefix='/query')

# 单库查询
api_bp.register_blueprint(opengauss_query_bp, url_prefix='/query/opengauss')
api_bp.register_blueprint(hive_query_bp, url_prefix='/query/hive')
api_bp.register_blueprint(neo4j_query_bp, url_prefix='/query/neo4j')

# 也可以在这里添加其他API蓝图
# api_bp.register_blueprint(another_bp, url_prefix='/another')