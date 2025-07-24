"""
统一的API响应格式
"""
from flask import jsonify
from datetime import datetime
from typing import Any, Optional

class APIResponse:
    """统一的API响应类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", status_code: int = 200):
        """成功响应"""
        response = {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str, error_code: Optional[str] = None, status_code: int = 400, data: Any = None):
        """错误响应"""
        response = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code
    
    @staticmethod
    def not_found(message: str = "资源未找到"):
        """404响应"""
        return APIResponse.error(message, "NOT_FOUND", 404)
    
    @staticmethod
    def server_error(message: str = "服务器内部错误"):
        """500响应"""
        return APIResponse.error(message, "INTERNAL_ERROR", 500)
    
    @staticmethod
    def validation_error(message: str = "输入数据无效"):
        """验证错误响应"""
        return APIResponse.error(message, "VALIDATION_ERROR", 400)

class TodoAppException(Exception):
    """自定义异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_response(self):
        """转换为API响应"""
        return APIResponse.error(self.message, self.error_code, self.status_code)