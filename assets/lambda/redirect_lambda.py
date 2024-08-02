import json
import boto3
import redis
import os

dynamodb = boto3.resource('dynamodb')
url_mappings_table = dynamodb.Table(os.getenv('TABLE_NAME'))
cache = redis.Redis(host=os.getenv('REDIS_ENDPOINT'), port=os.getenv('REDIS_PORT'))

def lambda_handler(event, context):
    short_url = event['pathParameters']['shortUrl']
    print(short_url)
    response = url_mappings_table.get_item(Key={'shortUrl': short_url})
    if 'Item' in response:
        long_url = response['Item']['longUrl']
        
    else:
        print('not found in db')
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'URL not found'})
        }    
    print(long_url)
    
    url_mappings_table.update_item(
        Key={'shortUrl': short_url},
        UpdateExpression='ADD accessCount :inc',
        ExpressionAttributeValues={':inc': 1}
    )
    
    return {
        'statusCode': 301,
        'headers': {'Location': long_url}
    }
