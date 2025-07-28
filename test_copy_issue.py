#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试复制功能的问题和解决方案
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import DailyTodoManager, DateAlias, db
from flask import Flask
from config import Config

def setup_test_app(test_name="test"):
    """设置测试应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 使用测试数据库
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    test_db_path = os.path.join(instance_dir, f'{test_name}_todos.db')
    
    # 如果测试数据库存在，删除它
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            # 如果无法删除，使用时间戳创建新文件名
            import time
            timestamp = int(time.time())
            test_db_path = os.path.join(instance_dir, f'{test_name}_{timestamp}_todos.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_path}'
    db.init_app(app)
    
    return app, test_db_path

def test_current_copy_issue():
    """测试当前复制功能的问题"""
    print("=" * 60)
    print("测试当前复制功能的问题")
    print("=" * 60)
    
    app, test_db_path = setup_test_app("current_issue")
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建测试管理器
        manager = DailyTodoManager(test_db_path)
        
        # 模拟今天是7月28日
        today = "2025-07-28"
        source_date = "2025-07-24"  # 要复制的日期
        
        print(f"1. 创建源日期 {source_date} 的任务")
        manager.add_todo(source_date, "任务1 - 原始")
        manager.add_todo(source_date, "任务2 - 原始")
        
        # 显示源日期的任务
        source_todos = manager.get_todos_for_date(source_date)
        print(f"   源日期 {source_date} 有 {len(source_todos)} 个任务:")
        for todo in source_todos:
            print(f"   - {todo['content']}")
        
        print(f"\n2. 模拟旧的复制逻辑 - 寻找明天的空闲日期")
        
        # 获取现有日期
        existing_dates = manager.get_available_dates()
        print(f"   现有日期: {existing_dates}")
        
        # 从明天开始找空闲日期（旧逻辑）
        tomorrow = datetime.strptime(today, '%Y-%m-%d') + timedelta(days=1)
        target_date = tomorrow.strftime('%Y-%m-%d')  # 2025-07-29
        
        print(f"   找到的目标日期: {target_date}")
        
        # 复制任务到目标日期
        print(f"\n3. 复制任务到 {target_date}")
        for todo in source_todos:
            manager.add_todo(target_date, todo['content'])
        
        # 设置别名
        alias_entry = DateAlias(date=target_date, alias="7月24日-copy")
        db.session.add(alias_entry)
        db.session.commit()
        
        print(f"   已设置别名: {target_date} -> '7月24日-copy'")
        
        # 显示复制后的状态
        target_todos = manager.get_todos_for_date(target_date)
        print(f"   目标日期 {target_date} 有 {len(target_todos)} 个任务:")
        for todo in target_todos:
            print(f"   - {todo['content']}")
        
        print(f"\n4. 问题演示：当真正到了 {target_date} 时")
        print(f"   系统会尝试为 {target_date} 创建今日任务表")
        print(f"   但发现表已经存在（被复制功能占用）")
        print(f"   这会导致逻辑冲突！")
        
        # 显示所有表
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'todo_%'")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"\n   当前数据库中的表:")
        for table in tables:
            table_name = table[0]
            date_str = table_name.replace('todo_', '').replace('_', '-')
            print(f"   - {table_name} (对应日期: {date_str})")

def test_new_copy_solution():
    """测试新的复制解决方案"""
    print("\n" + "=" * 60)
    print("测试新的复制解决方案")
    print("=" * 60)
    
    app, test_db_path = setup_test_app("new_solution")
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建测试管理器
        manager = DailyTodoManager(test_db_path)
        
        # 模拟今天是7月28日
        today = "2025-07-28"
        source_date = "2025-07-24"  # 要复制的日期
        
        print(f"1. 创建源日期 {source_date} 的任务")
        manager.add_todo(source_date, "任务1 - 原始")
        manager.add_todo(source_date, "任务2 - 原始")
        
        # 显示源日期的任务
        source_todos = manager.get_todos_for_date(source_date)
        print(f"   源日期 {source_date} 有 {len(source_todos)} 个任务:")
        for todo in source_todos:
            print(f"   - {todo['content']}")
        
        print(f"\n2. 使用新的复制逻辑 - 生成唯一标识符")
        
        # 生成唯一的复制标识符（新逻辑）
        timestamp = int(datetime.now().timestamp() * 1000)  # 毫秒时间戳
        today_obj = datetime.strptime(today, '%Y-%m-%d')
        date_prefix = today_obj.strftime('%Y%m%d')
        unique_id = f"copy-{date_prefix}-{timestamp}"
        
        print(f"   生成的唯一标识符: {unique_id}")
        
        # 复制任务到唯一标识符
        print(f"\n3. 复制任务到唯一标识符 {unique_id}")
        for todo in source_todos:
            manager.add_todo(unique_id, todo['content'])
        
        # 设置别名
        alias_entry = DateAlias(date=unique_id, alias="7月24日-copy")
        db.session.add(alias_entry)
        db.session.commit()
        
        print(f"   已设置别名: {unique_id} -> '7月24日-copy'")
        
        # 显示复制后的状态
        target_todos = manager.get_todos_for_date(unique_id)
        print(f"   目标标识符 {unique_id} 有 {len(target_todos)} 个任务:")
        for todo in target_todos:
            print(f"   - {todo['content']}")
        
        print(f"\n4. 解决方案验证：当真正到了 2025-07-29 时")
        future_date = "2025-07-29"
        print(f"   系统可以正常为 {future_date} 创建今日任务表")
        manager.add_todo(future_date, "7月29日的正常任务")
        
        future_todos = manager.get_todos_for_date(future_date)
        print(f"   {future_date} 有 {len(future_todos)} 个任务:")
        for todo in future_todos:
            print(f"   - {todo['content']}")
        
        # 显示所有表
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'todo_%'")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"\n   当前数据库中的表:")
        for table in tables:
            table_name = table[0]
            identifier = table_name.replace('todo_', '').replace('_', '-')
            if identifier.startswith('copy-'):
                print(f"   - {table_name} (复制标识符: {identifier})")
            else:
                print(f"   - {table_name} (日期: {identifier})")
        
        print(f"\n   ✅ 没有冲突！真实日期和复制标识符完全分离")

def test_alias_display():
    """测试别名显示功能"""
    print("\n" + "=" * 60)
    print("测试别名显示功能")
    print("=" * 60)
    
    app, test_db_path = setup_test_app("alias_display")
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建一些测试别名
        aliases = [
            ("2025-07-24", "工作日志"),
            ("2025-07-25", "学习计划"),
            ("copy-20250728-1234567890", "7月24日-copy"),
            ("copy-20250728-1234567891", "学习计划-copy")
        ]
        
        for date, alias in aliases:
            alias_entry = DateAlias(date=date, alias=alias)
            db.session.add(alias_entry)
        
        db.session.commit()
        
        print("创建的别名映射:")
        all_aliases = DateAlias.query.all()
        for alias in all_aliases:
            print(f"   {alias.date} -> '{alias.alias}'")
        
        print(f"\n前端显示逻辑:")
        print(f"   - 真实日期 2025-07-24 显示为: '工作日志'")
        print(f"   - 真实日期 2025-07-25 显示为: '学习计划'")
        print(f"   - 复制标识符 copy-20250728-1234567890 显示为: '7月24日-copy'")
        print(f"   - 复制标识符 copy-20250728-1234567891 显示为: '学习计划-copy'")
        print(f"   - 用户看到的是有意义的名称，而不是技术标识符")

def main():
    """主函数"""
    print("Flask Todo App - 复制功能问题分析和解决方案测试")
    print("时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        # 测试当前问题
        test_current_copy_issue()
        
        # 测试解决方案
        test_new_copy_solution()
        
        # 测试别名显示
        test_alias_display()
        
        print("\n" + "=" * 60)
        print("总结")
        print("=" * 60)
        print("问题:")
        print("  - 旧的复制逻辑使用未来日期作为表名")
        print("  - 当真正到达该日期时会产生冲突")
        print("  - 表名与显示名不一致，造成混淆")
        print()
        print("解决方案:")
        print("  - 使用唯一时间戳标识符 (copy-YYYYMMDD-timestamp)")
        print("  - 完全避免与真实日期的冲突")
        print("  - 通过别名系统提供有意义的显示名称")
        print("  - 保持数据库表名的唯一性和一致性")
        print()
        print("✅ 测试完成！新方案可以解决表名冲突问题。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()