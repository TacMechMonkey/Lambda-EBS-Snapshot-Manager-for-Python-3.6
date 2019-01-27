*** This is a fork of a 2017 repo I took down in Feb 18, which was since forked by https://github.com/yurplan/Lambda_EBS_Backups.

#### AWS has recently introduced the AWS LifeCycle Manager, which does *exactly* what this code does, minus a few things. This code can obv be run in all regions and also produces:
 - An email alert of which EBS volumes were snapshotted as below and sends it to you via simple AWS SNS email
 - Maps the snapshot times to your local (non-UTC) time
 - Enables created snapshots to be tagged with meaningful info for future cleanups
 - Enables the creation of daily snapshots which *can* be deleted, or monthly archive snapshots with no deletion date

This code is plug and play. If you don't need the SNS notifications, comment out/delete lines 118 to 128 of the daily function.

AWS' Lifecycle Manager is available at: https://aws.amazon.com/blogs/aws/new-lifecycle-management-for-amazon-ebs-snapshots/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+AmazonWebServicesBlog+%28Amazon+Web+Services+Blog%29

#### Deets:
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

 - If you're using this function for several hundred/thousand volumes, split the volumes into multple functions so they don't time out part way through. Or use a step function.

 - If you're unfamiliar with Python, be cautious editing the inst_list list, msg variable etc that creates the list for the SNS notification. If you tab it incorrectly and create a loop, you'll recieve thousands of emails until the function terminates.



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

ITC571
