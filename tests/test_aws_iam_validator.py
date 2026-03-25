from botocore.exceptions import ClientError, SSLError

from infratest.models import AWSIAMTestDefinition, TestType as InfraTestType
from infratest.validators.aws_iam_validator import execute_aws_iam_test


def test_execute_aws_iam_test_passes_when_access_is_granted(monkeypatch) -> None:
    class FakeClient:
        def head_bucket(self, **kwargs):
            assert kwargs == {"Bucket": "demo-bucket"}
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    class FakeSession:
        def client(self, service_name, region_name=None, config=None):
            assert service_name == "s3"
            assert region_name == "us-east-1"
            return FakeClient()

    monkeypatch.setattr(
        "infratest.validators.aws_iam_validator.boto3.Session",
        lambda: FakeSession(),
    )

    result = execute_aws_iam_test(
        AWSIAMTestDefinition(
            name="bucket-access",
            type=InfraTestType.AWS_IAM,
            service="s3",
            operation="head_bucket",
            region="us-east-1",
            parameters={"Bucket": "demo-bucket"},
            expect_access=True,
        )
    )

    assert result.status.value == "PASS"
    assert result.actual == "access granted"


def test_execute_aws_iam_test_passes_when_denial_is_expected(monkeypatch) -> None:
    class FakeClient:
        def head_bucket(self, **kwargs):
            raise ClientError(
                {
                    "Error": {
                        "Code": "AccessDenied",
                        "Message": "denied",
                    }
                },
                "HeadBucket",
            )

    class FakeSession:
        def client(self, service_name, region_name=None, config=None):
            return FakeClient()

    monkeypatch.setattr(
        "infratest.validators.aws_iam_validator.boto3.Session",
        lambda: FakeSession(),
    )

    result = execute_aws_iam_test(
        AWSIAMTestDefinition(
            name="bucket-denied",
            type=InfraTestType.AWS_IAM,
            service="s3",
            operation="head_bucket",
            parameters={"Bucket": "demo-bucket"},
            expect_access=False,
            expected_error_codes=["AccessDenied"],
        )
    )

    assert result.status.value == "PASS"
    assert result.actual == "AccessDenied"


def test_execute_aws_iam_test_returns_fail_result_for_sdk_ssl_errors(monkeypatch) -> None:
    class FakeClient:
        def list_functions(self, **kwargs):
            raise SSLError(endpoint_url="https://lambda.us-east-1.amazonaws.com", error="EOF")

    class FakeSession:
        def client(self, service_name, region_name=None, config=None):
            return FakeClient()

    monkeypatch.setattr(
        "infratest.validators.aws_iam_validator.boto3.Session",
        lambda: FakeSession(),
    )

    result = execute_aws_iam_test(
        AWSIAMTestDefinition(
            name="lambda-list-functions",
            type=InfraTestType.AWS_IAM,
            service="lambda",
            operation="list_functions",
            region="us-east-1",
            expect_access=True,
        )
    )

    assert result.status.value == "FAIL"
    assert result.metadata["error_type"] == "botocore_error"
    assert result.actual == "SSLError"