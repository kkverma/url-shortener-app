import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
url_mappings_table = dynamodb.Table(os.getenv('TABLE_NAME'))

def lambda_handler(event, context):
    short_url = event['pathParameters']['shortUrl']
    print(short_url)
    response = url_mappings_table.get_item(Key={'shortUrl': short_url})
    if 'Item' in response:
        item = response['Item']
        return {
            'statusCode': 200,
            'body': json.dumps({
                'longUrl': item['longUrl'],
                'accessCount': str(item.get('accessCount', 0)),
                'createdAt': str(item['createdAt'])
            })
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'URL not found'})
        }
