# AWS Cheat Commands

## Login Check

```powershell
aws sts get-caller-identity
aws configure get region
```

## Run The Broad Read-Only AWS Validation Suite

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
$env:PYTHONPATH='src'
c:/Users/lokeshwar.reddy/Infra_test/.venv/Scripts/python.exe -m infratest.cli verify examples/aws-account-readonly-checks.yaml --context aws --output both --output-path artifacts/aws-readonly-report.json
```

## Run The Local Smoke Suite

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
$env:PYTHONPATH='src'
c:/Users/lokeshwar.reddy/Infra_test/.venv/Scripts/python.exe scripts/manual_smoke_server.py
```

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
$env:PYTHONPATH='src'
c:/Users/lokeshwar.reddy/Infra_test/.venv/Scripts/python.exe -m infratest.cli verify examples/local-smoke.yaml --context local --output both --output-path artifacts/local-smoke/report.json
```

## Run The Generic Repo Sample

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
$env:PYTHONPATH='src'
c:/Users/lokeshwar.reddy/Infra_test/.venv/Scripts/python.exe -m infratest.cli verify infra-test.yaml --context public --output both --output-path artifacts/infratest/report.json
```

## Core AWS Inventory Commands

```powershell
aws ec2 describe-vpcs --region us-east-1 --query "{Count:length(Vpcs),Sample:Vpcs[:5].[VpcId,CidrBlock,IsDefault]}" --output json
aws elbv2 describe-load-balancers --region us-east-1 --query "{Count:length(LoadBalancers),Sample:LoadBalancers[:5].[LoadBalancerName,Scheme,Type,DNSName]}" --output json
aws rds describe-db-instances --region us-east-1 --query "{Count:length(DBInstances),Sample:DBInstances[:5].[DBInstanceIdentifier,Engine,PubliclyAccessible,Endpoint.Address]}" --output json
aws s3api list-buckets --query "{Count:length(Buckets),Sample:Buckets[:10].Name}" --output json
aws dynamodb list-tables --region us-east-1 --query "{Count:length(TableNames),Sample:TableNames[:10]}" --output json
aws ecs list-clusters --region us-east-1 --query "{Count:length(clusterArns),Sample:clusterArns[:10]}" --output json
aws eks list-clusters --region us-east-1 --query "{Count:length(clusters),Sample:clusters[:10]}" --output json
aws apigateway get-rest-apis --region us-east-1 --query "{Count:length(items),Sample:items[:10].[name,id]}" --output json
aws apigatewayv2 get-apis --region us-east-1 --query "{Count:length(Items),Sample:Items[:10].[Name,ApiId,ProtocolType]}" --output json
aws sqs list-queues --region us-east-1 --query "{Count:length(QueueUrls),Sample:QueueUrls[:10]}" --output json
aws sns list-topics --region us-east-1 --query "{Count:length(Topics),Sample:Topics[:10].TopicArn}" --output json
aws secretsmanager list-secrets --region us-east-1 --query "{Count:length(SecretList),Sample:SecretList[:10].Name}" --output json
aws ssm describe-parameters --region us-east-1 --query "{Count:length(Parameters),Sample:Parameters[:10].Name}" --output json
aws ecr describe-repositories --region us-east-1 --query "{Count:length(repositories),Sample:repositories[:10].repositoryName}" --output json
aws cloudfront list-distributions --query "{Count:length(DistributionList.Items),Sample:DistributionList.Items[:10].[Id,DomainName,Enabled]}" --output json
aws route53 list-hosted-zones --query "{Count:length(HostedZones),Sample:HostedZones[:10].[Name,Config.PrivateZone]}" --output json
aws logs describe-log-groups --region us-east-1 --query "{Count:length(logGroups),Sample:logGroups[:10].logGroupName}" --output json
aws elasticache describe-cache-clusters --region us-east-1 --show-cache-node-info --query "{Count:length(CacheClusters),Sample:CacheClusters[:10].[CacheClusterId,Engine,CacheClusterStatus]}" --output json
```