import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Mailer configuration
SENDER = os.getenv("SENDER")
RECIPIENT = os.getenv("RECIPIENT")
ROLE_ARN = os.getenv("ROLE_ARN")
SESSION_NAME = os.getenv("SESSION_NAME")

if not all([SENDER, RECIPIENT, ROLE_ARN, SESSION_NAME]):
    raise ValueError("Missing required environment variables. Check your .env file.")


def assume_role(role_arn, session_name):
    sts_client = boto3.client("sts")
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )

    return response["Credentials"]

role_arn = ROLE_ARN
session_name = SESSION_NAME

# Assume the role
credentials = assume_role(role_arn, session_name)

# Create an SES client using temporary credentials
ses_client = boto3.client(
    "ses", 
    region_name=AWS_REGION,
    aws_access_key_id=credentials["AccessKeyId"],
    aws_secret_access_key=credentials["SecretAccessKey"],
    aws_session_token=credentials["SessionToken"]
)

def send_email(subject, content):

    try:
        response = ses_client.send_email(
            Source=SENDER,
            Destination={
                "ToAddresses": [RECIPIENT],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": "",
                        "Charset": "UTF-8"
                    },
                    "Html": {
                        "Data": content,
                        "Charset": "UTF-8"
                    }
                }
            }
        )
    except ClientError as e:
        logger.error(f"Error: {e.response['Error']['Message']}")
    else:
        logger.info(f"Email sent! Message ID: {response['MessageId']}")

