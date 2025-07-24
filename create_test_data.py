#!/usr/bin/env python3
"""
创建测试数据 - 自动生成最近一周的7个表和示例任务
"""


from datetime import datetime, timedelta
from models import DailyTodoManager
import random

def create_test_data():
    """创建最近一周的测试数据"""
    manager = DailyTodoManager()
    
    # 示例任务内容
    sample_tasks = [
        "完成项目文档",
        "开会讨论需求",
        "代码审查",
        "修复bug #123",
        "更新用户手册",
        "测试新功能",
        "优化数据库查询",
        "回复客户邮件",
        "准备演示文稿",
        "学习新技术",
        "整理代码仓库",
        "写单元测试",
        "部署到测试环境",
        "分析性能问题",
        "更新依赖包"
    ]
    
    print("正在创建最近一周的测试数据...")
    
    # 创建最近7天的数据（包括今天）
    for i in range(7):
        # 计算日期（从6天前到今天）
        date = datetime.now() - timedelta(days=6-i)
        date_str = date.strftime('%Y-%m-%d')
        
        print(f"创建 {date_str} 的测试数据...")
        
        # 为每个日期随机创建2-5个任务
        num_tasks = random.randint(2, 5)
        selected_tasks = random.sample(sample_tasks, num_tasks)
        
        for task_content in selected_tasks:
            task_id = manager.add_todo(date_str, task_content)
            
            # 随机设置一些任务为已完成（30%的概率）
            if random.random() < 0.3:
                manager.update_todo(date_str, task_id, completed=True)
        
        print(f"  ✓ 创建了 {num_tasks} 个任务")
    
    print("\n测试数据创建完成！")
    print("现在你可以测试删除功能了。")
    
    # 显示创建的数据统计
    counts = manager.get_todo_counts()
    print("\n当前数据统计:")
    for date_str, count in sorted(counts.items(), reverse=True):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        display_date = date_obj.strftime('%m月%d日')
        print(f"  {display_date}: {count} 个任务")

if __name__ == "__main__":
    create_test_data()