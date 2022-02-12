import boto3
from botocore.exceptions import ClientError
import datetime as dt
import json
import os
iam = boto3.client('iam')
secrets_manager = boto3.client('secretsmanager')
user_name = os.environ['IAM_USER_NAME']
key_expiry_age = int(os.environ['EXPIRE_KEY_AFTER_DAYS'])
def create_key(user_name):
    try:
        access_key = iam.create_access_key(UserName=user_name)
        access_key_id = access_key['AccessKey']['AccessKeyId']
        secret_access_key = access_key['AccessKey']['SecretAccessKey']
        # json_access_key = json.dumps({'aws_access_key_id': access_key_id, 'aws_secret_access_key': secret_access_key})
        # # secrets_manager.update_secret(
        # #     SecretId=user_name,
        # #     SecretString=json_access_key
        # # )
        # secrets_manager.update_secret(
        # SecretId=user_name,
        # SecretString=json_access_key
              
        # )
        response = secrets_manager.get_secret_value(
        SecretId=user_name,
        # MaxResults=40,
        # IncludeDeprecated=True|False
        )
        #print(response['SecretString'])
        res = json.loads(response['SecretString'])
        res["aws_access_key_id"] =access_key_id
        res["aws_secret_access_key"]=secret_access_key
        json_access_key = json.dumps(res)
        secrets_manager.update_secret(
        SecretId=user_name,
        SecretString=json_access_key
        )
        print(res)
    except ClientError as e:
        print(e)
def deactivate_key(access_key, user_name):
    try:
        iam.update_access_key(
            UserName=user_name,
            AccessKeyId=access_key,
            Status='Inactive'
        )
        print(access_key + ' has been deactivated.')
    except ClientError as e:
        print(e)
def delete_key(access_key, user_name):
    try:
        iam.delete_access_key(
            UserName=user_name,
            AccessKeyId=access_key
        )
        print(access_key + ' has been deleted.')
    except ClientError as e:
        print(e)
def lambda_handler(event, context):
    print(f'Checking if access keys need to be rotated for {user_name}')
    try:
        access_keys = iam.list_access_keys(UserName=user_name)
        if not access_keys['AccessKeyMetadata']:
            print(f'No access keys found for user {user_name}')
        for key in access_keys['AccessKeyMetadata']:
            key_id = key['AccessKeyId']
            if key['Status'] == 'Inactive':
                print(f'Access key {key_id} is inactive, deleting key...')
                delete_key(key_id, user_name)
            else:
                key_date = key['CreateDate'].date()
                key_age = dt.date.today() - key_date
                if key_age.days >= key_expiry_age:
                    print(f'Access key {key_id} is more than {key_expiry_age} days old, deactivating key...')
                    deactivate_key(key_id, user_name)
                    print('Generating new access key...')
                    create_key(user_name)
                else:
                    print(f'Access key {key_id} is less than {key_expiry_age} days old, nothing to do.')
    except ClientError as e:
        print(e)
