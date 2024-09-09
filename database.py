import os
import sqlite3
from contextlib import closing
from config import DATABASE


def get_db_connection():
    """
    获取数据库连接
    """
    return sqlite3.connect(DATABASE)


def init_db():
    """
    初始化数据库，创建表
    """
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS media_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    media TEXT,  -- JSON 格式存储为 TEXT
                    response TEXT,  -- JSON 格式存储为 TEXT
                    success INTEGER NOT NULL DEFAULT 0,  -- 0 表示失败，1 表示成功
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')


def check_and_initialize_db():
    """
    检查数据库文件是否存在，不存在则初始化数据库
    """
    if not os.path.exists(DATABASE):
        print(f"Database file {DATABASE} does not exist. Initializing...")
        init_db()
    else:
        print(
            f"Database file {DATABASE} already exists. Skipping initialization.")
