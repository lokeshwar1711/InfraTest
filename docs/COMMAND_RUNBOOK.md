# InfraTest Command Runbook

This document lists the commands needed to install, validate, and manually smoke-test the repository.

## 1. Create Or Activate The Virtual Environment

Windows PowerShell:

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
```

## 2. Install InfraTest And Development Dependencies

```powershell
pip install -e .[dev]
```

## 3. Run The Full Automated Test Suite

```powershell
pytest
```

## 4. Run A Sample Public-Network Verification

This uses the repository sample file and writes both console and JSON output.

```powershell
infratest verify infra-test.yaml --context public --output both --output-path artifacts\infratest\report.json
```

## 5. Start The Local Smoke Servers

Open a second PowerShell terminal and run:

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
python scripts\manual_smoke_server.py
```

This starts:

- an HTTP health endpoint at `http://127.0.0.1:8765/health`
- a raw TCP listener at `127.0.0.1:8766`

## 6. Run The Local HTTP + TCP Smoke Suite

In another terminal:

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
infratest verify examples\local-smoke.yaml --context local --output both --output-path artifacts\local-smoke\report.json
```

## 7. Run The AWS Runtime Credential Smoke Test

Only run this after AWS credentials are available in the shell.

Examples:

- `aws configure`
- assumed role credentials in environment variables
- an IAM role on a runner or VM

Command:

```powershell
cd C:\Users\lokeshwar.reddy\Infra_test\InfraTest
infratest verify examples\aws-iam-smoke.yaml --context aws --output both --output-path artifacts\aws-smoke\report.json
```

## 8. Run Only JSON Output For CI Artifacts

```powershell
infratest verify infra-test.yaml --context public --output json --output-path artifacts\ci\infratest-report.json
```

## 9. Expected Exit Codes

- `0` means all blocking checks passed
- `1` means one or more blocking checks failed
- `2` means configuration or execution error

## 10. Suggested Manual Verification Sequence

Use this order when validating repository changes end to end:

```powershell
pytest
python scripts\manual_smoke_server.py
infratest verify examples\local-smoke.yaml --context local
infratest verify infra-test.yaml --context public --output both --output-path artifacts\infratest\report.json
infratest verify examples\aws-iam-smoke.yaml --context aws --output both --output-path artifacts\aws-smoke\report.json
```