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


@pytest.fixture
def fake_analyzer():
    """Reusable test double for AIAnalyzer with call tracking."""

    class FakeAnalyzer:
        def __init__(self):
            self.called = False
            # Return value can be overridden per-test
            self.return_value: dict[str, object] = {
                "match_score": "85/100",
                "missing_required": [],
            }

        def analyze_job(self, resume: str, description: str) -> dict:
            self.called = True
            return self.return_value

    return FakeAnalyzer()
