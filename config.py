import os
from datetime import timedelta

# 获取项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 应用配置
    APP_NAME = "Flask Todo App"
    APP_VERSION = "1.0.0"
    
    # 数据库配置
    DB_POOL_SIZE = 10
    DB_TIMEOUT = 30
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = timedelta(hours=1)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'todos_dev.db')
    
    # 开发环境特定配置
    TESTING = False
    WTF_CSRF_ENABLED = False  # 开发时禁用CSRF

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'todos.db')
    
    # 生产环境特定配置
    TESTING = False
    WTF_CSRF_ENABLED = True

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

