from flask import Flask, render_template
from models import db, DateAlias
from routes import todo_bp, ensure_today_todo_file
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 修改数据库URI为新数据库
import os
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_dir, exist_ok=True)  # 确保instance目录存在
db_path = os.path.join(instance_dir, 'todos_new.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)

# 注册 API 蓝图
app.register_blueprint(todo_bp)

# 主页路由只负责提供 HTML 页面
# JavaScript 会通过 API /api/todos 获取数据
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
     
    # 自动创建测试数据（最近一周的7个表）
    from create_test_data import create_test_data

    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表已创建")
    
    # 确保今天的todo文件存在
    ensure_today_todo_file()
   
    # create_test_data()

    # 临时调试，端口是 5990
    # 开机运行，端口是 5995
    app.run(debug=True, port=5990)