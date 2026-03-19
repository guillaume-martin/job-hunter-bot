import logging
import os
from typing import TypedDict

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


class AWSCredentials(TypedDict):
    """Temporary AWS credentials returned by STS AssumeRole

    Attributes:
       AccessKeyId: The temporary access key ID.
       SecretAccessKey: The temporary secret access key.
       SessionToken: The token required to authenticate with the credentials.
       Expiration: The datetime when the credentials expire.
    """

    AccessKeyId: str
    SecretAccessKey: str
    SessionToken: str
    Expiration: str  # ISO 8601 datetime string from STS


def assume_role(role_arn: str, session_name: str) -> AWSCredentials:
    """Assume an IAM role and return temporary credentials.

    Args:
        role_arn (str): The ARN of the IAM role to assume.
        session_name (str): An identifier for the assumed role session.

    Returns:
        A dict containing AccessKeyId, SecretAccessKey, and SessionToken.

    Raises:
        ClientError: If the STS AssumeRole call fails.
    """
    sts_client = boto3.client("sts")
    response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)

    credentials: AWSCredentials = response["Credentials"]
    return credentials


def _get_ses_client():
    """Build a boto3 SES client using assumed-role credential.

    Credentials are fetched at call time, never at import time.

    Returns:
        A boto3 SES client.
    """

    role_arn = ROLE_ARN
    session_name = SESSION_NAME

    # Assume the role
    credentials = assume_role(role_arn, session_name)

    return boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )


def send_email(subject: str, content: str) -> None:
    """Send an email via AWS SES.

    Args:
        subject (str): The email subject line
        content (str): The HTML body of the email
    """
    ses_client = _get_ses_client()
    try:
        response = ses_client.send_email(
            Source=SENDER,
            Destination={
                "ToAddresses": [RECIPIENT],
            },
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": "", "Charset": "UTF-8"},
                    "Html": {"Data": content, "Charset": "UTF-8"},
                },
            },
        )
    except ClientError as e:
        logger.exception(f"{e.response['Error']['Message']}")
    else:
        logger.info(f"Email sent! Message ID: {response['MessageId']}")
