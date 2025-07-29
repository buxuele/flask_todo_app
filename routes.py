"""
新的路由文件 - 支持每日一表架构
"""
from flask import Blueprint, request, jsonify, send_file
from models import DailyTodoManager, DateAlias, db
from datetime import datetime
import os

# 使用 'api' 作为蓝图名称，并添加 URL 前缀
todo_bp = Blueprint('api', __name__, url_prefix='/api')

# 全局todo管理器实例
todo_manager = DailyTodoManager()

def _is_valid_date_format(date_str):
    """验证日期格式是否为YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def ensure_today_todo_file():
    """确保今天的todo文件和数据库表存在"""
    today = datetime.now().strftime('%Y-%m-%d')
    date_obj = datetime.strptime(today, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%m.%d')
    
    # 1. 确保今天的数据库表存在
    table_name = todo_manager.create_table_for_date(today)
    print(f"已确保今日数据库表存在: {table_name}")
    
    # 2. 创建docs文件夹
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    filename = f"{formatted_date}-todo.md"
    filepath = os.path.join(docs_dir, filename)
    
    # 3. 如果文件不存在，创建一个空的todo文件
    if not os.path.exists(filepath):
        content = f"# {formatted_date} Todo\n\n今日无任务\n\n---\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建今日Todo文件: {filename}")
    else:
        print(f"今日Todo文件已存在: {filename}")

@todo_bp.route('/todos', methods=['GET'])
def get_todos():
    """获取指定日期的todos"""
    date = request.args.get('date')
    if not date:
        # 如果没有指定日期，返回今天的todos
        date = datetime.now().strftime('%Y-%m-%d')
    
    todos = todo_manager.get_todos_for_date(date)
    return jsonify(todos)

@todo_bp.route('/todos', methods=['POST'])
def add_todo():
    """添加新的todo"""
    data = request.json
    content = data.get('content')
    date = data.get('date') or datetime.now().strftime('%Y-%m-%d')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    todo_id = todo_manager.add_todo(date, content)
    
    # 返回新创建的todo
    todos = todo_manager.get_todos_for_date(date)
    new_todo = next((t for t in todos if t['id'] == todo_id), None)
    
    if new_todo:
        return jsonify(new_todo), 201
    else:
        return jsonify({'error': 'Failed to create todo'}), 500

@todo_bp.route('/todos/counts', methods=['GET'])
def get_todo_counts():
    """获取每个日期的todo数量"""
    counts = todo_manager.get_todo_counts()
    return jsonify(counts)

@todo_bp.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """获取单个todo - 需要日期参数"""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    todos = todo_manager.get_todos_for_date(date)
    todo = next((t for t in todos if t['id'] == todo_id), None)
    
    if todo:
        return jsonify(todo)
    else:
        return jsonify({'error': 'Todo not found'}), 404

@todo_bp.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新todo"""
    data = request.json
    date = data.get('date')
    
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    update_data = {}
    if 'content' in data:
        update_data['content'] = data['content']
    if 'completed' in data:
        update_data['completed'] = data['completed']
    if 'order' in data:
        update_data['order_num'] = data['order']
    
    success = todo_manager.update_todo(date, todo_id, **update_data)
    
    if success:
        # 返回更新后的todo
        todos = todo_manager.get_todos_for_date(date)
        updated_todo = next((t for t in todos if t['id'] == todo_id), None)
        return jsonify(updated_todo)
    else:
        return jsonify({'error': 'Todo not found or update failed'}), 404

@todo_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """删除单个todo"""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    success = todo_manager.delete_todo(date, todo_id)
    
    if success:
        return '', 204
    else:
        return jsonify({'error': 'Todo not found'}), 404

@todo_bp.route('/todos/<int:todo_id>/copy', methods=['POST'])
def copy_todo(todo_id):
    """复制todo"""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    # 获取原todo
    todos = todo_manager.get_todos_for_date(date)
    original_todo = next((t for t in todos if t['id'] == todo_id), None)
    
    if not original_todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    # 复制到同一日期
    new_todo_id = todo_manager.add_todo(date, original_todo['content'])
    
    # 返回新创建的todo
    todos = todo_manager.get_todos_for_date(date)
    new_todo = next((t for t in todos if t['id'] == new_todo_id), None)
    
    return jsonify(new_todo), 201

@todo_bp.route('/todos/date/<date>', methods=['DELETE'])
def delete_todos_by_date(date):
    """删除指定日期的所有todos"""
    count = todo_manager.delete_all_todos_for_date(date)
    
    # 同时删除该日期的别名
    try:
        alias = DateAlias.query.filter_by(date=date).first()
        if alias:
            db.session.delete(alias)
            db.session.commit()
    except Exception as e:
        # 别名删除失败不影响主要功能
        print(f"删除日期别名失败: {e}")
    
    return jsonify({'message': f'已删除 {count} 个任务', 'count': count})

@todo_bp.route('/todos/copy-date', methods=['POST'])
def copy_date_todos():
    """复制整个日期的todos到新日期"""
    data = request.json
    source_date = data.get('source_date')
    target_date = data.get('target_date')
    
    if not source_date or not target_date:
        return jsonify({'error': 'Source date and target date are required'}), 400
    
    # 获取源日期的所有todos
    source_todos = todo_manager.get_todos_for_date(source_date)
    
    # 即使没有任务也要创建目标日期的表
    copied_count = 0
    if source_todos:
        # 复制到目标日期
        for todo in source_todos:
            todo_manager.add_todo(target_date, todo['content'])
            copied_count += 1
    else:
        # 即使源日期没有任务，也要确保目标日期的表存在
        # 通过创建表来实现"复制空列表"
        todo_manager.create_table_for_date(target_date)
    
    return jsonify({
        'message': f'已复制 {copied_count} 个任务',
        'count': copied_count
    })

@todo_bp.route('/date-aliases', methods=['GET'])
def get_date_aliases():
    """获取所有日期别名"""
    try:
        aliases = DateAlias.query.all()
        return jsonify({alias.date: alias.alias for alias in aliases})
    except Exception as e:
        print(f"获取日期别名失败: {e}")
        return jsonify({})

@todo_bp.route('/date-aliases', methods=['POST'])
def set_date_alias():
    """设置或更新日期别名"""
    data = request.json
    date = data.get('date')
    alias = data.get('alias')
    
    if not date or not alias:
        return jsonify({'error': 'Date and alias are required'}), 400
    
    # 验证日期格式 - 支持标准日期格式和复制表的唯一标识符格式
    if not (date.startswith('copy-') or _is_valid_date_format(date)):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD or copy-* format'}), 400
    
    try:
        # 查找现有别名或创建新的
        existing_alias = DateAlias.query.filter_by(date=date).first()
        if existing_alias:
            existing_alias.alias = alias
        else:
            new_alias = DateAlias(date=date, alias=alias)
            db.session.add(new_alias)
        
        db.session.commit()
        return jsonify({'message': 'Date alias updated successfully'})
    except Exception as e:
        print(f"设置日期别名失败: {e}")
        return jsonify({'error': str(e)}), 500

@todo_bp.route('/date-aliases/<date>', methods=['DELETE'])
def delete_date_alias(date):
    """删除日期别名"""
    try:
        alias = DateAlias.query.filter_by(date=date).first()
        if alias:
            db.session.delete(alias)
            db.session.commit()
            return jsonify({'message': 'Date alias deleted successfully'})
        else:
            return jsonify({'error': 'Date alias not found'}), 404
    except Exception as e:
        print(f"删除日期别名失败: {e}")
        return jsonify({'error': str(e)}), 500

@todo_bp.route('/todos/export/<date>', methods=['GET'])
def export_todo(date):
    """导出指定日期的todos为markdown文件"""
    todos = todo_manager.get_todos_for_date(date)
    
    # 创建docs文件夹
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    # 生成markdown内容
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%m.%d')
    
    content = f"# {formatted_date} Todo\n\n"
    
    if not todos:
        content += "今日无任务\n"
    else:
        completed_todos = [t for t in todos if t['completed']]
        pending_todos = [t for t in todos if not t['completed']]
        
        if pending_todos:
            content += "## 待完成\n\n"
            for todo in pending_todos:
                content += f"- [ ] {todo['content']}\n"
            content += "\n"
        
        if completed_todos:
            content += "## 已完成\n\n"
            for todo in completed_todos:
                content += f"- [x] {todo['content']}\n"
            content += "\n"
        
        content += f"---\n总计: {len(todos)} 项任务，已完成: {len(completed_todos)} 项\n"
    
    # 保存文件
    filename = f"{formatted_date}-todo.md"
    filepath = os.path.join(docs_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return send_file(filepath, as_attachment=True, download_name=filename)