from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # 载入配置
    app.config.from_object('config')

    # 注册蓝图或路由
    from .routes import main
    app.register_blueprint(main)

    return app