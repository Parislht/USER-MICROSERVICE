import boto3
import hashlib
import uuid
import os
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    print(event)

    try:
        tenant_id = event['body']['tenant_id']
        username = event['body']['username']
        password = event['body']['password']
        hashed_password = hash_password(password)

        # Obtener nombres de tablas desde variables de entorno
        tabla_usuarios = os.environ['TABLE_NAME_USERS']
        tabla_token = os.environ['TABLE_NAME_TOKENS']

        # Acceder a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_users = dynamodb.Table(tabla_usuarios)

        # Buscar usuario con tenant_id y username
        response = table_users.get_item(
            Key={
                'tenant_id': tenant_id,
                'username': username
            }
        )

        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': 'Usuario no existe en este tenant'
            }

        print(response)

        user_item = response['Item']
        hashed_password_db = user_item['password']

        # Validar password
        if hashed_password != hashed_password_db:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }

        # Generar token
        token = str(uuid.uuid4())
        fecha_hora_exp = datetime.utcnow() + timedelta(minutes=200)

        table_tokens = dynamodb.Table(tabla_token)
        table_tokens.put_item(
            Item={
                'tenant_id': tenant_id,
                'token': token,
                'username': username,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        responseMessage = {
            'statusCode': 200,
            'body': {
                'message': 'Login exitoso',
                'token': token,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S'),
                'tenant_id': tenant_id,
                'username': username
            }
        }
        print("Mensaje de respuesta:")
        print(responseMessage)

        return responseMessage

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }
