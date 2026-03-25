# AWS Discovery Findings

## Session

- Account: `172694458017`
- Principal: `arn:aws:sts::172694458017:assumed-role/ADFS-MHF-MI-TechOps/lokeshwar.reddy@spglobal.com`
- Region used for discovery: `us-east-1`

## Inventory Snapshot

- VPCs: `27`
- ELBv2 load balancers: `15`
- RDS instances: `11`
- S3 buckets: `409`
- DynamoDB tables: `38`
- ECS clusters: `9`
- EKS clusters: `2`
- API Gateway REST APIs: `23`
- API Gateway v2 APIs: `5`
- SQS queues: `78`
- SNS topics: `60`
- Secrets Manager secrets: `1496`
- SSM parameters: `408`
- ECR repositories: `73`
- CloudFront distributions: `62`
- Route 53 hosted zones: `118`
- CloudWatch log groups: `1129`
- ElastiCache clusters: `2`

## Safe Validation Run

Report file:

- [artifacts/aws-readonly-report.json](C:/Users/lokeshwar.reddy/Infra_test/InfraTest/artifacts/aws-readonly-report.json)

Outcome:

- Total tests: `36`
- Passed: `32`
- Failed: `4`
- Blocking failures: `1`
- Advisory failures: `3`

## Blocking Failure

- `sqs-list-queues`
  - Failure type: Python SDK SSL transport failure
  - Error: `UNEXPECTED_EOF_WHILE_READING`

## Advisory Failures

- `lambda-list-functions`
  - Failure type: Python SDK SSL transport failure
- `sqs-get-adolfd-unified-queue-attrs`
  - Failure type: Python SDK SSL transport failure
- `kms-list-keys`
  - Failure type: Python SDK SSL transport failure

## Interpretation

- The account has broad active usage across network, compute, storage, messaging, secrets, and edge services.
- Most read-only boto3 validations succeeded with the current credentials.
- The remaining failures are not permission-denied responses; they are transport-layer SSL issues specific to the Python runtime path used by InfraTest in this environment.
- AWS CLI read-only commands for several of these services succeeded earlier in the same login session, which suggests an environment or trust-store difference between AWS CLI and the Python runtime rather than an IAM problem.

## Immediate Next Check

- Compare Python runtime CA handling with AWS CLI CA handling before treating the SQS, Lambda, or KMS results as IAM failures.