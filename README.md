# Virtual Embedded Test Platform (VETP)

**Builder Edition — Version 1 | Python · Verilog · SQLite · Optional AWS Integration · Streamlit**

The Virtual Embedded Test Platform (VETP) is a software-based engineering test environment for simulating, testing and investigating the behavior of a digital protection controller.

VETP combines Verilog simulation with Python test automation. It executes predefined engineering scenarios, compares the simulated controller's behavior with expected results, saves the evidence in SQLite and JSON, generates Markdown reports and provides a Streamlit dashboard for reviewing test history.

Optional publication workflows can share validated campaign summaries through a local HTTP receiver or private Amazon S3 storage.

## What the project demonstrates

- Finite-state-machine design and protection logic in Verilog.
- Automated digital simulation using Icarus Verilog.
- Python-driven test cases, fault injection and expected-versus-actual verification.
- Persistent engineering test records using SQLite.
- Structured JSON logs and Markdown engineering reports.
- Interactive inspection through a Streamlit dashboard.
- Optional campaign publication and remote artifact-integrity verification.

The VETP is an educational and portfolio engineering platform, not a certified hardware protection system or production cloud service.

## System architecture

```
Engineering Test Cases
         |
         v
Python Test Runner
         |
         v
Icarus Verilog Simulation
         |
         v
Controller Outputs
         |
         v
Expected vs. Actual Verification
         |
         v
Persistent Test Evidence
 (SQLite / JSON / Reports)
         |
         +----> Streamlit Dashboard
         |
         +----> Campaign Summary
                    |
                    v
          Optional Publication
           (Local / HTTP / S3)
```

The core protection-controller states are IDLE, STARTUP, RUNNING, FAULT and RECOVERY. The test suite includes scenarios involving startup behavior and electrical fault conditions.

## Repository Structure

| Directory | Purpose |
|---|---|
| `hdl/` | Verilog protection-controller modules and testbenches |
| `src/` | Python simulation orchestration, verification, and campaign execution |
| `tests/` | Automated Python tests |
| `dashboard/` | Streamlit dashboard |
| `docs/` | Architecture diagrams, screenshots, and supporting documentation |
| `build/` | Generated test artifacts, SQLite database, and reports |

The `build/` directory contains generated evidence and is not required to understand the source-code architecture. It is not included.

## Technologies

| Technology | Role |
|---|---|
| Python | Test automation, verification, reporting and integration |
| Verilog | Digital protection-controller implementation |
| Icarus Verilog | HDL compilation and simulation |
| GTKWave | Optional waveform inspection |
| SQLite | Local engineering evidence storage |
| Streamlit | Dashboard and test-result inspection |
| Pytest | Automated testing |
| Boto3 | Optional private S3 publication |

## Prerequisites

- Windows PowerShell
- Python and pip
- Icarus Verilog (`iverilog` and `vvp`)
- Git, if cloning the repository
- Optional: GTKWave for waveform inspection
- Optional: AWS CLI and authorized AWS credentials for live S3 publication

## Installation

From the repository root, create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Confirm the main tools:

```powershell
python --version
iverilog -V
vvp -V
```

Icarus Verilog must be installed separately and available on the system PATH.

## Run automated tests

```powershell
python -m pytest -q
```

Tests that execute Verilog simulations require working `iverilog` and `vvp` executables.

### Verifying the local test environment

From the **same PowerShell terminal** used to run pytest, check that the executables are discoverable:

```powershell
Get-Command iverilog
Get-Command vvp
iverilog -V
vvp -V
python -m pytest -q
```

### Local Verification Results

The VETP automated test suite and engineering campaign were executed successfully in a local Windows development environment.

- **Environment:** Windows / PowerShell
- **Python version:** [3.14.0]
- **Icarus Verilog version:** [12.0]
- **Test command:** `python -m pytest -q`
- **Pytest result:** 76 passed, 0 failed, 0 skipped
- **Engineering campaign:** 8 passed, 0 failed
- **Last verified:** 11/23/2026

| Test ID | Engineering Scenario | Result |
|---|---|---|
| TC-001 | Normal Startup | PASS |
| TC-002 | Nominal Operation | PASS |
| TC-003 | Brief Undervoltage Transient | PASS |
| TC-004 | Sustained Undervoltage | PASS |
| TC-005 | Overcurrent Shutdown | PASS |
| TC-006 | Overtemperature Shutdown | PASS |
| TC-007 | Simultaneous OC and OT | PASS |
| TC-008 | Fault Reset and Recovery | PASS |

All eight engineering scenarios passed in the reported local execution.

Reproduction: Run python -m pytest -q followed by python .\src\persistent_campaign.py in local publication mode, using the installation instructions above.

These results demonstrate successful execution in the documented local environment. 

## Run the engineering campaign

Use local publication mode:

```powershell
$env:VETP_CLOUD_MODE = "local"
```

Run the full engineering campaign:

```powershell
python .\src\persistent_campaign.py
```

The campaign executes the engineering test cases, saves SQLite evidence, generates JSON logs and Markdown reports, and prepares a validated local campaign summary.

The default SQLite database is:

```text
build/vetp.db
```

Running the campaign again creates additional engineering records. Preserve existing evidence before conducting a new demonstration.

## Launch the dashboard

```powershell
python -m streamlit run .\dashboard\app.py
```

Use the local URL printed by Streamlit.

The dashboard provides Overview, Test History, Run Inspector and Analysis workspaces.

## Generated evidence

The `build/` directory contains generated engineering artifacts, including the SQLite database, FPGA input/output files, JSON test logs, Markdown reports, campaign summaries and optional cloud publication artifacts.

Generated evidence should be treated separately from source code. Do not publish credentials or private operational data.

## Documentation

- [System Architecture Diagram](docs/VETP_Architecture_Diagram.png)
- [Dashboard Overview](docs/Dashboard_Overview1.png)
- [Dashboard Test History](docs/Dashboard_Test_History.png)
- [Dashboard Run Inspector](docs/Dashboard_Run_Inspector_1.png)
- [Dashboard Analysis](docs/Dashboard_Analysis1.png)
- [Light-Cloud Demonstration Guide](docs/VETP_Light_Cloud_Demo_Guide.md)

A complete-system demonstration video is planned but is not included in this repository snapshot.

## Scope and limitations

Version 1 uses a simulated Verilog controller, not a connected physical microcontroller.

SQLite is the local evidence database. The dashboard uses Streamlit. The HTTP receiver is intended for local demonstration, and live S3 publication is optional.

Electrical measurement-history visualization and advanced cloud infrastructure are outside the current verified core workflow.

### Local HTTP Receiver — Security Scope

VETP includes an optional HTTP receiver for demonstrating the publication and inspection of engineering test evidence.

The receiver is explicitly bound to `127.0.0.1:8000` and is intended for local development and demonstration only.

- The receiver is not designed for public internet deployment.
- Authentication and production-grade access controls are not implemented.
- Requests undergo basic JSON and engineering-schema validation.
- The receiver should not be exposed through public interfaces, port forwarding, or public tunnels.
- The receiver is not required for the core Verilog simulation, Python verification, SQLite evidence storage, or Streamlit dashboard.

Future versions may introduce stronger request validation, authentication, and secure remote deployment mechanisms.

**Security boundary:** The local HTTP receiver is an educational integration component, not a production-ready API service.

## Project purpose

VETP was developed as a hands-on engineering project for exploring digital protection logic, automated verification, persistent test evidence and integration between hardware simulation and software tools.

The emphasis is on understanding the engineering workflow, not merely executing a collection of technologies.