"""
OpenGauss 模块初始化
"""
from app.models.opengauss.connection import OpenGaussConnection
from app.models.opengauss.models import OpenGaussModel
from app.models.opengauss.queries import OpenGaussQueries

__all__ = ['OpenGaussConnection', 'OpenGaussModel', 'OpenGaussQueries']
