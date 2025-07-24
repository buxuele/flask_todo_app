"""
统一的数据库服务层
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """统一的数据库服务"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """确保数据库文件存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作并返回影响的行数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """执行插入操作并返回新记录的ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,))
        return len(result) > 0
    
    def create_table(self, table_name: str, schema: str):
        """创建表"""
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        self.execute_update(query)
    
    def drop_table(self, table_name: str):
        """删除表"""
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_update(query)