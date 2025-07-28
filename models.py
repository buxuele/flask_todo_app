"""
新的数据库模型 - 每天一个表的设计
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import os
import uuid

db = SQLAlchemy()

class TableRegistry(db.Model):
    """表注册表 - 记录所有todo表的元信息"""
    __tablename__ = 'table_registry'
    
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.String(36), nullable=False, unique=True)  # UUID
    display_name = db.Column(db.String(100), nullable=False)  # 显示名称
    table_type = db.Column(db.String(20), default='daily')  # 表类型: daily, copy
    source_date = db.Column(db.String(10), nullable=True)  # 原始日期（如果是日期表）
    source_table_id = db.Column(db.String(36), nullable=True)  # 复制来源表ID
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)  # 是否活跃

    def to_dict(self):
        return {
            'id': self.id,
            'table_id': self.table_id,
            'display_name': self.display_name,
            'table_type': self.table_type,
            'source_date': self.source_date,
            'source_table_id': self.source_table_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class DateAlias(db.Model):
    """日期别名表 - 兼容旧系统"""
    __tablename__ = 'date_aliases'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False, unique=True)  # 格式: YYYY-MM-DD
    alias = db.Column(db.String(50), nullable=False)  # 自定义别名
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'alias': self.alias,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DailyTodoManager:
    """每日Todo管理器 - 处理动态表操作，支持UUID表名"""
    
    def __init__(self, db_path='instance/todos_new.db'):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """确保数据库文件存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_table_name_by_id(self, table_id):
        """根据表ID生成实际的表名"""
        return f"todo_{table_id.replace('-', '_')}"
    
    def get_table_name(self, date_str):
        """兼容旧系统：根据日期或唯一标识符生成表名"""
        # 处理新的复制标识符格式：copy-YYYYMMDD-timestamp
        # 以及传统日期格式：YYYY-MM-DD
        return f"todo_{date_str.replace('-', '_')}"
    
    def create_table_for_date(self, date_str):
        """为指定日期创建表（简化版本，兼容旧系统和新的复制标识符）"""
        table_name = self.get_table_name(date_str)
        self._create_physical_table(table_name)
        return table_name
    
    def create_copy_table(self, source_table_id, display_name):
        """创建复制表"""
        from flask import current_app
        with current_app.app_context():
            # 生成新的UUID
            new_table_id = str(uuid.uuid4())
            
            # 创建注册记录
            registry_entry = TableRegistry(
                table_id=new_table_id,
                display_name=display_name,
                table_type='copy',
                source_table_id=source_table_id
            )
            
            db.session.add(registry_entry)
            db.session.commit()
            
            # 创建实际的数据库表
            new_table_name = self.get_table_name_by_id(new_table_id)
            self._create_physical_table(new_table_name)
            
            return new_table_id, new_table_name
    
    def _create_physical_table(self, table_name):
        """创建物理数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            order_num INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME NULL
        )
        """
        
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
    
    def format_date_for_display(self, date_str):
        """格式化日期用于显示"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%m月%d日')
        except:
            return date_str
    
    def table_exists_by_id(self, table_id):
        """检查指定表ID的表是否存在"""
        table_name = self.get_table_name_by_id(table_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """, (table_name,))
        
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    def table_exists(self, date_str):
        """检查指定日期的表是否存在（兼容旧系统）"""
        table_name = self.get_table_name(date_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """, (table_name,))
        
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    def get_todos_by_table_id(self, table_id):
        """根据表ID获取todos"""
        if not self.table_exists_by_id(table_id):
            return []
        
        table_name = self.get_table_name_by_id(table_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
        SELECT id, content, completed, order_num, created_at, completed_at
        FROM {table_name}
        ORDER BY order_num, id
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        todos = []
        for row in rows:
            todos.append({
                'id': row[0],
                'content': row[1],
                'completed': bool(row[2]),
                'order': row[3],
                'table_id': table_id,
                'created_at': row[4],
                'completed_at': row[5]
            })
        
        return todos
    
    def get_todos_for_date(self, date_str):
        """获取指定日期的所有todos（兼容旧系统）"""
        if not self.table_exists(date_str):
            return []
        
        table_name = self.get_table_name(date_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
        SELECT id, content, completed, order_num, created_at, completed_at
        FROM {table_name}
        ORDER BY order_num, id
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        todos = []
        for row in rows:
            todos.append({
                'id': row[0],
                'content': row[1],
                'completed': bool(row[2]),
                'order': row[3],
                'date': date_str,
                'created_at': row[4],
                'completed_at': row[5]
            })
        
        return todos
    
    def add_todo_by_table_id(self, table_id, content, order_num=None):
        """根据表ID添加新的todo"""
        if not self.table_exists_by_id(table_id):
            return None
        
        table_name = self.get_table_name_by_id(table_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 如果没有指定order，获取最大值+1
        if order_num is None:
            cursor.execute(f"SELECT MAX(order_num) FROM {table_name}")
            max_order = cursor.fetchone()[0] or 0
            order_num = max_order + 1
        
        cursor.execute(f"""
        INSERT INTO {table_name} (content, completed, order_num, created_at)
        VALUES (?, ?, ?, ?)
        """, (content, 0, order_num, datetime.now().isoformat()))
        
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return todo_id

    def add_todo(self, date_str, content, order_num=None):
        """添加新的todo（兼容旧系统和新的复制标识符）"""
        # 对于复制标识符，直接创建表，不需要注册表逻辑
        if date_str.startswith('copy-'):
            table_name = self.get_table_name(date_str)
            self._create_physical_table(table_name)
        else:
            # 确保表存在（传统日期格式）
            table_name = self.create_table_for_date(date_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 如果没有指定order，获取最大值+1
        if order_num is None:
            cursor.execute(f"SELECT MAX(order_num) FROM {table_name}")
            max_order = cursor.fetchone()[0] or 0
            order_num = max_order + 1
        
        cursor.execute(f"""
        INSERT INTO {table_name} (content, completed, order_num, created_at)
        VALUES (?, ?, ?, ?)
        """, (content, 0, order_num, datetime.now().isoformat()))
        
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return todo_id
    
    def update_todo(self, date_str, todo_id, **kwargs):
        """更新todo（支持日期和复制标识符）"""
        if not self.table_exists(date_str):
            return False
        
        table_name = self.get_table_name(date_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建更新语句
        update_fields = []
        values = []
        
        if 'content' in kwargs:
            update_fields.append('content = ?')
            values.append(kwargs['content'])
        
        if 'completed' in kwargs:
            update_fields.append('completed = ?')
            values.append(kwargs['completed'])
            
            # 如果设置完成状态，同时更新完成时间
            if kwargs['completed']:
                update_fields.append('completed_at = ?')
                values.append(datetime.now().isoformat())
            else:
                update_fields.append('completed_at = ?')
                values.append(None)
        
        if 'order_num' in kwargs:
            update_fields.append('order_num = ?')
            values.append(kwargs['order_num'])
        
        if not update_fields:
            conn.close()
            return False
        
        values.append(todo_id)
        
        cursor.execute(f"""
        UPDATE {table_name}
        SET {', '.join(update_fields)}
        WHERE id = ?
        """, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_todo(self, date_str, todo_id):
        """删除todo"""
        if not self.table_exists(date_str):
            return False
        
        table_name = self.get_table_name(date_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (todo_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_all_todos_for_date(self, date_str):
        """删除指定日期的所有todos并删除表"""
        if not self.table_exists(date_str):
            return 0
        
        table_name = self.get_table_name(date_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先获取任务数量
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # 删除整个表，而不是只删除数据
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        conn.close()
        
        return count
    
    def get_available_dates(self):
        """获取所有有数据的日期和标识符"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'todo_%'
        ORDER BY name DESC
        """)
        
        tables = cursor.fetchall()
        conn.close()
        
        dates = []
        for table in tables:
            table_name = table[0]
            # 从表名恢复原始标识符
            identifier = table_name.replace('todo_', '').replace('_', '-')
            dates.append(identifier)
        
        return dates
    
    def get_todo_counts(self):
        """获取每个日期的todo数量"""
        dates = self.get_available_dates()
        counts = {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for date_str in dates:
            table_name = self.get_table_name(date_str)
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            counts[date_str] = cursor.fetchone()[0]
        
        conn.close()
        return counts

# 全局实例
todo_manager = DailyTodoManager()