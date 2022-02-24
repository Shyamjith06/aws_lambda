import json
import boto3
region ="eu-west-1"

def lambda_handler(event, context):
    non_compliant_sgs = []
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()
    sglist=response['SecurityGroups']
    for sg in sglist:
        sgrules=sg['IpPermissions']
        for ipranges in sgrules:
            ips=ipranges['IpRanges']
            for cidr in ips:
                if cidr['CidrIp'] == '0.0.0.0/0':
                    non_compliant_sgs.append(sg['GroupName'])
                    #print(sg['GroupName'])
                #break;
                    #print(sg['GroupName'])
    if len(non_compliant_sgs) != 0:
        final_list = list(dict.fromkeys(non_compliant_sgs))
        print(final_list)
        
