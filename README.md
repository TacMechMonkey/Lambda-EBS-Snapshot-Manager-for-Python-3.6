Use Boto3 and Lambda to schedule the creation and clearing of EBS snapshots, with SNS (email, txt...) notifications.

 - To tag an EBS volume for backup, add a tag "LambdaBackup" for the daily function, or "LambdaArchive" for the monthly function, with a value of how often to snapshot. Values for "Backup" key: Hourly, 4/day, Daily, Weekly, No

 - Optionally, add a "Retention" tag to EBS volumes with the number of days to override the default amount in the function. Values for "Retention" tag is in days, and only works for the daily function (the monthly function doesn't delete).

 - Snapshots will be created with a tag key: "Delete After", value: seconds to exists after creation. After this period, they're purged. If no key is set, they're purged after the default retention period you set.

 - Snapshots will be named "Backup of vol-1234asdf1234asdf (Volume Name)".
    
 - Enter an SNS topic ARN to recieve emails, txt notifications etc of the snapshots created:
    
    
#### Notes:
 - 4/day snapshots will run 0000, 0600, 1200, 1800 in UTC time. If you need to change this, add the time difference to current_hour, ie +10 hours for Brisbane = if backup_mod is False or (current_hour + 10) % backup_mod != 0:

 - This script will only snapshot volumes which are 'in-use'. If a volume is detached or in another state, it won't. You can change this by deleting the line {'Name': 'status', 'Values': 'in-use'},

 - If you stop an instance, this script will still snapshot the attached volumes if they're tagged. If previous snapshots have been taken of the volume, you won't be billed for additional storage since snapshots are incremental, it will just clog up your snapshots in AWS.

If you know a way to modify this to only snapshot volumes attached to running instances, please let me know.



#### How to:
 - Create a new role with the IAM policy below 
 - Create Lambda function with below settings A
 - Create Lambda function with below settings A
 - Add code to Lambda 
 - Add SNS topic and subscribe to it 
 - Checkout CloudWatch logs to confirm nil errors


#### EBS Volume tagging example:

![Tagging Example](https://github.com/TacMechMonkey/Lambda_EBS_Backups-Python_3-6/blob/master/TaggingExample.PNG)



#### SNS Email Example:

![SNS Email Example](https://github.com/TacMechMonkey/Lambda_EBS_Backups-Python_3-6/blob/master/EmailExample.jpg)


#### Lambda config
 - Runtime: Python 3.6
 - Handler: lambda_function.lambda_handler or filename.lambda_handler
 - Role: As below
 - Memory: 128
 - Timeout: 360 sec
 - No VPC
 - Add an hourly trigger using "CloudWatch Events - Schedule" / cron(0 * ? * * *)


#### IAM Lambda Role:

{

    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:ap-southeast-2:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:Describe*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVolumes",
                "ec2:DescribeSnapshots",
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:CreateTags",
                "ec2:ModifySnapshotAttribute",
                "ec2:ResetSnapshotAttribute"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
