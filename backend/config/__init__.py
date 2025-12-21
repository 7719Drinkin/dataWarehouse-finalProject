"""
配置管理模块
"""
import os

class Config:
    """基础配置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False

    # API配置
    API_TITLE = 'Movie Data Warehouse API'
    API_VERSION = '1.0.0'

    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    DEVELOPMENT = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

