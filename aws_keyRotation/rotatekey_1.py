import boto3, datetime as dt
from botocore.exceptions import ClientError
import json
key_expiry_age=0
cli=iam = boto3.client('iam')
#iam = boto3.resource('iam')
res=cli.list_users()
#timeLimit=datetime.datetime.now() - datetime.timedelta( days = int(keyAge) )
#print(timeLimit.date())

def deactivate_key(access_key, user_name):
    try:
        cli.update_access_key(
            UserName=user_name,
            AccessKeyId=access_key,
            Status='Inactive'
        )
        print(access_key + ' has been deactivated.')
    except ClientError as e:
        print(e)


def create_key(user_name):
    try:
        access_key = iam.create_access_key(UserName=user_name)
        access_key_id = access_key['AccessKey']['AccessKeyId']
        secret_access_key = access_key['AccessKey']['SecretAccessKey']
        # json_access_key = json.dumps({'aws_access_key_id': access_key_id, 'aws_secret_access_key': secret_access_key})
        # secrets_manager.put_secret_value(
        #     SecretId=user_name,
        #     SecretString=json_access_key
        #)
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

for x in res['Users']:
    y=cli.list_access_keys(UserName=x['UserName'])
    if not y['AccessKeyMetadata']:
        print(f'No access keys found for user {user_name}')
    for k in y['AccessKeyMetadata']:
        key_id= k['AccessKeyId']
        user_name=k['UserName']
        key_date = k['CreateDate'].date()
        key_age = dt.date.today() - key_date
        if k['Status'] == 'Inactive':
            print(f'Access key {key_id} is inactive, deleting key...')
            delete_key(key_id, user_name)
        elif key_age.days >= key_expiry_age:
            print(f'Access key {key_id} is more than {key_expiry_age} days old, deactivating key...')
            deactivate_key(key_id, user_name)
            print('Generating new access key...')
            create_key(user_name)
        else:
            print(f'Access key {key_id} is less than {key_expiry_age} days old, nothing to do.')


# ###############

# access_keys = iam.list_access_keys(UserName=user_name)

#         if not access_keys['AccessKeyMetadata']:

#             print(f'No access keys found for user {user_name}')

#         for key in access_keys['AccessKeyMetadata']:

#             key_id = key['AccessKeyId']

# key_date = key['CreateDate'].date()

# else:

#                 key_date = key['CreateDate'].date()

#                 key_age = dt.date.today() - key_date


#                 if key_age.days >= key_expiry_age:

#                     print(f'Access key {key_id} is more than {key_expiry_age} days old, deactivating key...')

#                     deactivate_key(key_id, user_name)

#                     print('Generating new access key...')

#                     create_key(user_name)
