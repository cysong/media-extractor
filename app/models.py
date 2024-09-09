import json
from datetime import datetime
from database import get_db_connection

class MediaData:
    def __init__(self, url, media, response, success=False):
        self.url = url
        self.media = json.dumps(media, indent=4)  # 转换为 JSON 格式存储
        self.response = json.dumps(response, indent=4)  # 转换为 JSON 格式存储
        self.success = 1 if success else 0  # 1 表示成功，0 表示失败
        self.created_at = datetime.now()

    def save(self):
        """
        保存记录到数据库
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO media_data (url, media, response, success, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.url, self.media, self.response, self.success, self.created_at))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_id(record_id):
        """
        根据 ID 查询记录
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM media_data WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'url': row[1],
                    'media': json.loads(row[2]),  # 转换为字典格式返回
                    'response': json.loads(row[3]),  # 转换为字典格式返回
                    'success': bool(row[4]),  # 转换为布尔值
                    'created_at': row[5]
                }
            return None

    @staticmethod
    def list_all():
        """
        列出所有记录
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM media_data ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'url': row[1],
                    'media': json.loads(row[2]),
                    'response': json.loads(row[3]),
                    'success': bool(row[4]),
                    'created_at': row[5]
                }
                for row in rows
            ]

    @staticmethod
    def filter_by_created_at(start_date, end_date):
        """
        根据创建时间段查询
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM media_data 
                WHERE created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
            ''', (start_date, end_date))
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'url': row[1],
                    'media': json.loads(row[2]),
                    'response': json.loads(row[3]),
                    'success': bool(row[4]),
                    'created_at': row[5]
                }
                for row in rows
            ]

    @staticmethod
    def filter_by_success(success):
        """
        根据 success 字段过滤查询
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM media_data WHERE success = ? ORDER BY created_at DESC', (1 if success else 0,))
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'url': row[1],
                    'media': json.loads(row[2]),
                    'response': json.loads(row[3]),
                    'success': bool(row[4]),
                    'created_at': row[5]
                }
                for row in rows
            ]
