from app import app, db
from models import DateAlias, DailyTodoManager
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库"""
    try:
        with app.app_context():
            # 创建基础表（DateAlias表）
            db.create_all()
            
            # 初始化todo管理器
            todo_manager = DailyTodoManager()
            
            # 添加示例数据
            add_sample_data(todo_manager)
            
            print('数据库初始化完成，已添加示例数据')
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def add_sample_data(todo_manager):
    """添加示例数据"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 今天的任务
        today_todos = [
            "完成项目文档",
            "开会讨论需求", 
            "代码审查",
            "更新数据库设计",
            "测试新功能"
        ]
        
        # 为今天创建表并添加任务
        for i, content in enumerate(today_todos):
            todo_id = todo_manager.add_todo(today, content)
            # 第二个任务标记为已完成
            if i == 1:
                todo_manager.update_todo(today, todo_id, completed=True)
        
        # 昨天的任务（已完成）
        yesterday_todos = [
            "准备会议材料",
            "回复邮件",
            "整理代码"
        ]
        
        # 为昨天创建表并添加任务
        for content in yesterday_todos:
            todo_id = todo_manager.add_todo(yesterday, content)
            # 所有昨天的任务都标记为已完成
            todo_manager.update_todo(yesterday, todo_id, completed=True)
        
        # 添加日期别名示例
        with app.app_context():
            date_alias = DateAlias(
                date=yesterday,
                alias="昨日工作"
            )
            db.session.add(date_alias)
            db.session.commit()
        
        logger.info(f"成功添加 {len(today_todos)} 个今日任务和 {len(yesterday_todos)} 个昨日任务")
        
    except Exception as e:
        logger.error(f"添加示例数据失败: {str(e)}")
        raise

if __name__ == '__main__':
    init_database() 