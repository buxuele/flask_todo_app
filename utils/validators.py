"""
输入验证工具
"""
import re
from datetime import datetime
from functools import wraps
from flask import request
from utils.api_response import APIResponse, TodoAppException

def validate_json(*required_fields):
    """验证JSON请求数据的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return APIResponse.validation_error("请求必须是JSON格式")
            
            data = request.get_json()
            if not data:
                return APIResponse.validation_error("请求数据不能为空")
            
            # 检查必需字段
            missing_fields = []
            for field in required_fields:
                if field not in data or not data[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return APIResponse.validation_error(f"缺少必需字段: {', '.join(missing_fields)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_date_format(date_str: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_content(content: str) -> str:
    """验证任务内容"""
    if not content or not content.strip():
        raise TodoAppException("任务内容不能为空", "EMPTY_CONTENT")
    
    content = content.strip()
    if len(content) > 500:
        raise TodoAppException("任务内容不能超过500个字符", "CONTENT_TOO_LONG")
    
    # 检查是否包含恶意脚本
    if re.search(r'<script|javascript:|on\w+\s*=', content, re.IGNORECASE):
        raise TodoAppException("任务内容包含不允许的字符", "INVALID_CONTENT")
    
    return content

def validate_alias(alias: str) -> str:
    """验证别名"""
    if not alias or not alias.strip():
        raise TodoAppException("别名不能为空", "EMPTY_ALIAS")
    
    alias = alias.strip()
    if len(alias) > 100:
        raise TodoAppException("别名不能超过100个字符", "ALIAS_TOO_LONG")
    
    # 检查是否包含恶意脚本
    if re.search(r'<script|javascript:|on\w+\s*=', alias, re.IGNORECASE):
        raise TodoAppException("别名包含不允许的字符", "INVALID_ALIAS")
    
    return alias

def validate_date_param(f):
    """验证日期参数的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        date = request.args.get('date')
        if date and not validate_date_format(date):
            return APIResponse.validation_error("日期格式错误，请使用 YYYY-MM-DD 格式")
        return f(*args, **kwargs)
    return decorated_function