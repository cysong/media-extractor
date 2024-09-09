from flask import Flask

from database import check_and_initialize_db

def create_app():
    app = Flask(__name__)
    
    # 载入配置
    app.config.from_object('config')
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # 启用美化输出

    # 注册蓝图或路由
    from .routes import main
    app.register_blueprint(main)

    check_and_initialize_db()

    return app