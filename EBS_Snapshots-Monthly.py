# Original code from:
# https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups/
# http://blog.powerupcloud.com/2016/02/15/automate-ebs-snapshots-using-lambda-function/
# Rewritten to be configured on individual Volumes, not Instances:
# https://github.com/Brayyy/Lambda-EBS-Snapshot-Manager
# https://github.com/doximity/lambda-ebs-snapshots
# Updated for Python 3.6, added local time to 4/day, added requirement for EBS volume to be 'in-use', added SNS notifications:
# https://github.com/TacMechMonkey/Lambda_EBS_Backups-Python_3-6

import boto3
import datetime
import os

TIME_ZONE = 'Australia/Brisbane'
AWS_REGION = 'ap-southeast-2'
BACKUP_KEY = 'LambdaArchive'
SNSARN = 'arn:aws:sns:ap-southeast-2:YOURSNSARN:Monthly_Backups_Complete'

if 'TIME_ZONE' in os.environ:
    TIME_ZONE = os.environ['TIME_ZONE']
if 'AWS_REGION' in os.environ:
    AWS_REGION = os.environ['AWS_REGION']
if 'BACKUP_KEY' in os.environ:
    BACKUP_KEY = os.environ['BACKUP_KEY']

ec2_client = boto3.client('ec2', region_name=AWS_REGION)
sns = boto3.client('sns')
os.environ['TZ'] = TIME_ZONE

def create_snapshot():
    volumes = ec2_client.describe_volumes(
        Filters=[
            {'Name': 'tag-key', 'Values': [BACKUP_KEY]},
            {'Name': 'status', 'Values': ['in-use']},
        ]
    ).get(
        'Volumes', []
    )

    print("Number of volumes with backup tag: %d" % len(volumes))

    inst_list = []

    for volume in volumes:
        vol_id = volume['VolumeId']
        snap_date = datetime.datetime.now().strftime('%Y-%m-%d')
        snap_desc = vol_id

        for name in volume['Tags']:
            tag_key = name['Key']
            tag_val = name['Value']

            if tag_key == 'Name':
                snap_desc = vol_id + '(' + tag_val + ')'

        snap_name = 'Monthly backup of ' + snap_desc
        snap_desc = 'Monthly Lambda backup ' + snap_date + ' of ' + snap_desc

        print("%s is scheduled this month" % vol_id)

        for name in volume['Tags']:
            inst_tag_key = name['Key']
            inst_tag_val = name['Value']
            if inst_tag_key == 'Name':
                inst_list.append(inst_tag_val)
                    
        snap = ec2_client.create_snapshot(
            VolumeId=vol_id,
            Description=snap_desc
        )

        print("%s created" % snap['SnapshotId'])

        ec2_client.create_tags(
            Resources=[snap['SnapshotId']],
            Tags=[
                {'Key': 'Name', 'Value': snap_name}]
        )

    msg = str("\n".join(inst_list))

    if len(inst_list) == 0:
        message = sns.publish(
            TopicArn=SNSARN,
            Subject=("WARNING: NO MONTHLY SNAPSHOTS TAKEN!"),
            Message=("NO MONTHLY SNAPSHOTS TAKEN. Please notify the AWS SysAdmin immediately\n")
        )

        print("WARNING: {}".format(message))

    else:
        message = sns.publish(
            TopicArn=SNSARN,
            Subject=("Monthly Lambda snapshot function complete"),
            Message=("The following monthly archive snapshots have been created:\n\n" + msg + "\n")
        )
            
        print("Response: {}".format(message))


def lambda_handler(event, context):
    create_snapshot()

    return "Successful"
