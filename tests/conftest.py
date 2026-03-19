import boto3
import pytest
from moto import mock_aws


@pytest.fixture(autouse=True)
def mock_aws_services():
    """Intercepts all boto3 calls so tests never hit real AWS.

    Uses moto to spin up an in-memory AWS environment for every test.
    The mock is torn down automatically after each test.
    """
    with mock_aws():
        # Create a dummy IAM role so AssumeRole calls succeed
        iam = boto3.client("iam", region_name="us-east-1")
        iam.create_role(
            RoleName="RoleName",
            AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[]}',
        )
        yield
