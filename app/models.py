import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr

TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'media-extractor-records')

_table = None


def _get_table():
    global _table
    if _table is None:
        _table = boto3.resource('dynamodb').Table(TABLE_NAME)
    return _table


class MediaData:
    def __init__(self, url: str, response: dict, success: bool):
        self.id = str(uuid.uuid4())
        self.url = url
        self.response = json.dumps(response)
        self.success = success
        self.created_at = datetime.now(timezone.utc).isoformat()

    def save(self):
        _get_table().put_item(Item={
            'id': self.id,
            'url': self.url,
            'response': self.response,
            'success': self.success,
            'created_at': self.created_at,
        })
        return self.id

    @staticmethod
    def get_by_id(record_id: str):
        result = _get_table().get_item(Key={'id': record_id})
        return _parse(result.get('Item'))

    @staticmethod
    def list_all():
        result = _get_table().scan()
        items = sorted(result['Items'], key=lambda x: x['created_at'], reverse=True)
        return [_parse(item) for item in items]

    @staticmethod
    def filter_by_success(success: bool):
        result = _get_table().scan(
            FilterExpression=Attr('success').eq(success)
        )
        items = sorted(result['Items'], key=lambda x: x['created_at'], reverse=True)
        return [_parse(item) for item in items]


def _parse(item: dict):
    if not item:
        return None
    return {
        'id': item['id'],
        'url': item['url'],
        'response': json.loads(item['response']),
        'success': item['success'],
        'created_at': item['created_at'],
    }
