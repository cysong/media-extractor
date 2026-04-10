"""
Local test runner — simulates an API Gateway event.
Usage: python run_local.py <url>
"""
import json
import sys

from handler import lambda_handler

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://x.com/NASA/status/1'
    event = {'body': json.dumps({'url': url})}
    result = lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    print(json.dumps(json.loads(result['body']), indent=2))
