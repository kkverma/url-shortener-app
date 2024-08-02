import time
import json
import boto3
import hashlib
import random
import string
from redis import Redis  
import os

BASE62 = string.digits + string.ascii_letters
dynamodb = boto3.resource('dynamodb')
url_mappings_table = dynamodb.Table(os.getenv('TABLE_NAME'))
cache = Redis(host=os.getenv('REDIS_ENDPOINT'), port=os.getenv('REDIS_PORT'), decode_responses=True)

def base62_encode(num):
    if num == 0:
        return BASE62[0]
    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(BASE62[rem])
    base62.reverse()
    return ''.join(base62)

def generate_short_url(long_url, length=8):
    
    salt = ''.join(random.choices(BASE62, k=16))
    hash_object = hashlib.sha256((salt + long_url).encode())
    hash_digest = hash_object.digest()
    num = int.from_bytes(hash_digest[:8], 'big')
    short_url = base62_encode(num)[:length]
        
    cache.set(short_url, )
    url_mappings_table.put_item(
        Item={
            'shortUrl': short_url,
            'longUrl': long_url,
            'createdAt': str(int(time.time())),
            'accessCount': 0
        }
    )
    
    return short_url

def lambda_handler(event, context):
    body = json.loads(event['body'])
    long_url = body.get('longUrl')
    print(long_url)
    if not long_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input'})
        }
    print('long_url found')
    short_url = generate_short_url(long_url)
    print(short_url)
    return {
        'statusCode': 200,
        'body': json.dumps({'shortUrl': short_url})
    }
