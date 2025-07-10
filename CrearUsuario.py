import os
import boto3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    print("event: ", event)

    try:
        # Extraer campos desde el body
        username = event['username']
        password = event['password']
        tenant_id = event['tenant_id']

        # Obtener nombre de la tabla desde variable de entorno
        nombre_tabla = os.environ['TABLE_NAME_USERS']

        # Validación simple
        if username and password and tenant_id:
            hashed_password = hash_password(password)

            # Guardar en DynamoDB
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table(nombre_tabla)
            t_usuarios.put_item(
                Item={
                    'tenant_id': tenant_id,
                    'username': username,
                    'password': hashed_password
                }
            )

            mensaje = {
                'message': 'User registered successfully',
                'username': username,
                'tenant_id': tenant_id
            }
            return {
                'statusCode': 200,
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing username, password or tenant_id'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }
        return {
            'statusCode': 500,
            'body': mensaje
        }
