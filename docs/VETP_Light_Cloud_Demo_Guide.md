# VETP | Light-Cloud Demonstration Guide

**Virtual Embedded Test Platform (VETP)**  
**Audience:** Developers, reviewers, and engineering portfolio evaluators  
**Purpose:** Reproduce a genuine engineering campaign, inspect its local evidence, publish a validated campaign summary to private Amazon S3 storage, and verify the remote artifact's integrity.

This guide describes the operational workflow for the VETP. Commands are written for **Windows PowerShell**, executed from the repository root unless otherwise stated. Values such as `YOUR_BUCKET_NAME` are parameters supplied by the person running the demonstration, not previously verified results.

**Evidence standard:** Only report actual observed campaign IDs, test outcomes, paths, and cloud responses. Expected output examples are illustrative. A successful engineering campaign and a successful cloud publication are separate outcomes.

## A. Prerequisites and environment

### A1. Required components

- Windows PowerShell, Python, and an activated project virtual environment.
- Icarus Verilog (`iverilog`, `vvp`) for HDL simulation; SQLite through Python's built-in `sqlite3`.
- The VETP repository with engineering test cases, `src/persistent_campaign.py`, reporting and dashboard components, and the cloud modules (`cloud_integration.py`, `cloud_campaign.py`, `cloud_campaign_publisher.py`, `cloud_api_server.py`, `cloud_storage.py`, `cloud_workflow.py`, `cloud_receipts.py`).
- For S3 publication: Boto3, AWS CLI v2, an authorized AWS profile, and a private S3 bucket with permission to put and get objects under `vetp/campaigns/*`.

### A2. Confirm the environment

Open PowerShell at the repository root. If the virtual environment uses a different folder name, adjust the activation path.

```powershell
.\venv\Scripts\Activate.ps1
python --version
python -m pip check
iverilog -V
vvp -V
python -c "import sqlite3; print('SQLite:', sqlite3.sqlite_version)"
python -c "import boto3; print('Boto3:', boto3.__version__)"
```

Resolve missing tools and incompatible dependencies before continuing. Record the **observed** tool versions in `docs/vetp_demo_manifest.md`. Live AWS credentials are not required for local-only publication.

### A3. Check source syntax and automated tests

```powershell
python -m py_compile src/persistent_campaign.py src/cloud_workflow.py src/cloud_receipts.py src/cloud_storage.py
python -m pytest tests/test_cloud_campaign.py tests/test_cloud_storage.py tests/test_cloud_workflow.py -v
```

Run these as separate commands. If a named test file is absent, inspect the repository's `tests/` directory and run the corresponding existing test suite. Record the actual number of passed, failed, and skipped tests; do not infer a passing result from the presence of tests.

### A4. Configure a private S3 destination

Check the AWS CLI and the intended credential profile. The example profile name is replaceable.

```powershell
aws --version
aws sts get-caller-identity --profile YOUR_AWS_PROFILE
```

Configure the **same terminal session** that will launch the campaign:

```powershell
$env:VETP_CLOUD_MODE = "s3"
$env:VETP_S3_BUCKET = "YOUR_BUCKET_NAME"
$env:VETP_AWS_REGION = "YOUR_AWS_REGION"
$env:VETP_AWS_PROFILE = "YOUR_AWS_PROFILE"
```

Obtain the bucket name and region from the S3 console, and the profile name from the local AWS CLI configuration. For example, `us-east-2` is the AWS Ohio region. The profile must resolve to an identity permitted to upload and retrieve campaign objects. Keep S3 Block Public Access enabled. Never insert AWS secret keys into source files, `.env.example`, screenshots, or Git history.

## B. Local engineering demonstration

### B1. Execute a genuine campaign

```powershell
python src/persistent_campaign.py
```

The runner executes the configured HDL test cases, compares expected and observed behavior, generates real test-run logs, stores run evidence in SQLite, and produces campaign reports. The final cloud coordinator should execute once after the engineering campaign and its report have been generated.

Record the actual number of tests, PASS/FAIL outcomes, at least one run ID, the campaign ID, the report path, the local campaign JSON path, and the publication receipt path. Do not substitute fabricated evidence if a step fails.

### B2. Inspect saved engineering evidence

Look under `build/` for the SQLite database, HDL output, test-run logs, reports, validated campaign JSON, and publication receipts. Common artifact locations include:

```text
build/vetp.db
build/cloud_outbox/campaigns/campaign_<CAMPAIGN_ID>.json
build/cloud_receipts/
```

The exact SQLite database path must be confirmed from the runner's configuration. The following example uses `build/vetp.db` and opens an **existing** database in read-only mode; change the path if your project differs.

```powershell
@'
import sqlite3
from pathlib import Path
path = Path("build/vetp.db").resolve()
if not path.is_file():
    raise SystemExit(f"Database not found: {path}")
with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
    for (name,) in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ):
        print(name)
    print("test_runs columns:")
    for column in db.execute("PRAGMA table_info(test_runs)"):
        print(column)
'@ | python -
```

Inspect the JSON file using the campaign ID printed by the runner:

```powershell
$campaignId = "YOUR_CAMPAIGN_ID"
Get-Content "build/cloud_outbox/campaigns/campaign_$campaignId.json"
```

Compare its run IDs, test IDs, test outcomes, and counts with the persisted engineering evidence. The publication coordinator should reject a campaign whose claimed results contradict SQLite; the location of the verification helper may vary by implementation.

### B3. Review the dashboard

If the repository provides a Streamlit dashboard, locate its actual entry-point script and run it. For a dashboard stored at `src/dashboard.py`, the command would be:

```powershell
python -m streamlit run src/dashboard.py
```

This path is an **example**; use the dashboard file that exists in the repository. Open a genuine run, compare its result with the corresponding SQLite record and report, and stop Streamlit with `Ctrl + C` when finished.

## C. Cloud publication and integrity verification

### C1. Choose the publication mode

- **`local`** saves the campaign artifact locally without a remote request.
- **`api`** publishes to the locally hosted HTTP receiver; start `src/cloud_api_server.py` in a separate terminal before using it.
- **`s3`** publishes directly to private Amazon S3 using Boto3 and the configured AWS profile; the local HTTP receiver is **not** required.

This demonstration uses `s3`. Confirm the campaign runner calls `publish_completed_campaign()` only once; duplicate campaign-level publication logic can create conflicts or misleading receipts.

### C2. Run the integrated workflow

After setting the four S3 environment variables in Part A, execute:

```powershell
python src/persistent_campaign.py
```

A successful S3 publication may end with a block similar to:

```text
Final campaign cloud workflow:
  Campaign: CAMP-<generated-id>
  Engineering PASS: True
  Publication status: VERIFIED
  Publication message: <observed-message>
  Artifact: <actual-local-json-path>
  Receipt: <actual-receipt-path>
```

This is a **format example**, not a completed test record. `VERIFIED` should be reported only when the upload succeeds and the bytes downloaded from S3 have the same SHA-256 digest as the local artifact. An engineering FAIL can still be published and verified: cloud integrity does not turn a failed engineering test into a pass.

### C3. Independently inspect the S3 object

In the S3 console, navigate to the configured private bucket and the object key `vetp/campaigns/campaign_<CAMPAIGN_ID>.json`. Verify the campaign ID and keep public access blocked. For an additional manual integrity check, download the object to a **separate** filename:

```powershell
$bucket = "YOUR_BUCKET_NAME"
$campaignId = "YOUR_CAMPAIGN_ID"
$profile = "YOUR_AWS_PROFILE"
$localFile = "build/cloud_outbox/campaigns/campaign_$campaignId.json"
$downloadFile = "build/downloaded_campaign_check.json"

aws s3 cp `
  "s3://$bucket/vetp/campaigns/campaign_$campaignId.json" `
  $downloadFile `
  --profile $profile

Get-FileHash $localFile -Algorithm SHA256
Get-FileHash $downloadFile -Algorithm SHA256
```

Compare the two printed `Hash` values. They should be identical. The application's `verify_uploaded_campaign()` performs the equivalent programmatic local-versus-remote comparison; the manual check is independent corroboration.

### C4. Examine the publication receipt

Open the receipt path printed by the workflow. Confirm it contains the campaign identifier, engineering outcome, publication mode, publication status, message, and recorded attempt time where supported by `cloud_receipts.py`. A receipt documents **publication**, while the campaign JSON and SQLite database document **engineering**.

## D. Controlled failure and recovery

### D1. Objective

Demonstrate that a cloud publication error does not rewrite a genuine engineering result. Preserve the original campaign JSON and SQLite evidence. Do not change IAM policies, delete objects, or expose credentials to simulate failure.

### D2. Test an unavailable bucket safely

Prefer using an existing saved campaign artifact with the repository's saved-artifact upload helper, if its interface supports this. Check the actual script and its usage before invoking it; no unverified command-line signature is assumed here.

In a **separate PowerShell terminal**, configure a bucket name that does not exist in the account and restore the real configuration afterward:

```powershell
$env:VETP_CLOUD_MODE = "s3"
$env:VETP_S3_BUCKET = "vetp-nonexistent-demo-bucket-example-123456"
$env:VETP_AWS_REGION = "YOUR_AWS_REGION"
$env:VETP_AWS_PROFILE = "YOUR_AWS_PROFILE"
```

Run the repository's supported saved-artifact upload command with the **existing** campaign JSON. If no suitable command is provided, use a mocked S3 failure test instead. Do not rerun an entire FPGA campaign solely to force a cloud failure.

Expected behavior: the upload attempt reports failure; remote verification is not claimed; the original JSON and SQLite engineering outcomes remain unchanged. A publication receipt is expected only when the path under test actually uses the coordinator and receipt writer. Record the observed error and the method used to recover.

### D3. Other cases to consider

- **Engineering FAIL, S3 verified:** preserve engineering FAIL and report publication VERIFIED independently.
- **SQLite mismatch:** reject publication and investigate local evidence.
- **Rejected upload or invalid credentials:** report publication failure without modifying the campaign artifact.
- **Upload succeeded but download verification failed:** report an unverified outcome, not VERIFIED.
- **Duplicate object or uncertain network result:** inspect the existing object before retrying; do not silently overwrite or assume a failed upload.

## E. Completion checklist

- [ ] Real engineering campaign executed and outcomes recorded.
- [ ] HDL output, test logs, reports, and SQLite evidence inspected.
- [ ] Campaign run IDs, counts, and PASS/FAIL results agree with local evidence.
- [ ] Validated campaign JSON exists in the outbox.
- [ ] Campaign-level publication coordinator executed once.
- [ ] S3 upload used a restricted identity and private bucket.
- [ ] Remote object key and campaign ID match.
- [ ] Remote and local SHA-256 hashes match.
- [ ] Publication receipt exists and has been reviewed.
- [ ] Controlled failure preserved the engineering evidence.
- [ ] Relevant automated tests passed; actual results were recorded.
- [ ] `docs/vetp_demo_manifest.md` contains observed versions, IDs, paths, statuses, and findings.
- [ ] No credentials or generated private artifacts are staged for Git.

## F. Demonstration record

Complete `docs/vetp_demo_manifest.md` with actual software versions, executed test counts, campaign ID, relevant run IDs, SQLite evidence location, artifact and receipt paths, S3 object key, integrity verification result, and any failure observations. The manifest is the **record of a specific run**; this guide remains the **repeatable procedure**.

## G. Troubleshooting

- **`aws` not recognized:** install AWS CLI v2 and reopen PowerShell.
- **`NoCredentialsError`:** confirm the named profile and its credential source.
- **`AccessDenied`:** inspect IAM permissions, bucket restrictions, and the object prefix.
- **`NoSuchBucket`:** confirm bucket name, region, and AWS account.
- **HTTP 501 in API mode:** confirm the campaign endpoint is implemented and restart the receiver.
- **HTTP 409 or duplicate campaign:** inspect whether the campaign ID was previously received.
- **SQLite traceability error:** resolve missing or inconsistent records; never bypass validation.
- **`UNVERIFIED`:** inspect GetObject access, connectivity, and hash verification.
- **Missing receipt:** check `cloud_receipts.py`, the output path, and whether the coordinator completed.

## Scope

This procedure does not require a cloud-hosted SQLite replacement, public dashboard deployment, Kubernetes, or automatic synchronization infrastructure. It demonstrates the existing VETP engineering-to-cloud publication path and its evidence integrity.
