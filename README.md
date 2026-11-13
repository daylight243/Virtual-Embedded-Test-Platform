# Virtual Embedded Test Platform (VETP)

**Builder Edition — Version 1 | Python · Verilog · SQLite · AWS · Streamlit**

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

```text
Engineering Test Cases
          |
          v
Python Test Runner
          |
          v
Icarus Verilog Simulation
          |
          v
Actual Controller Outputs
          |
          v
Python Verification
          |
          v
JSON Logs + SQLite + Reports
          |
          +----> Streamlit Dashboard
          |
          +----> Validated Campaign Summary
                         |
                         v
                 Local / HTTP / S3
```

The core protection-controller states are IDLE, STARTUP, RUNNING, FAULT and RECOVERY. The test suite includes scenarios involving startup behavior and electrical fault conditions.

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

```

## Generated evidence

The `build/` directory contains generated engineering artifacts, including the SQLite database, FPGA input/output files, JSON test logs, Markdown reports, campaign summaries and optional cloud publication artifacts.

Generated evidence should be treated separately from source code. Do not publish credentials or private operational data.

## Documentation

- [Complete-System Demonstration](docs/demo_full_system.md)
- [Light-Cloud Demonstration Guide](docs/VETP_Light_Cloud_Demo_Guide.md)

## Scope and limitations

Version 1 uses a simulated Verilog controller, not a connected physical microcontroller.

SQLite is the local evidence database. The dashboard uses Streamlit. The HTTP receiver is intended for local demonstration, and live S3 publication is optional.

Electrical measurement-history visualization and advanced cloud infrastructure are outside the current verified core workflow.

## Project purpose

VETP was developed as a hands-on engineering project for exploring digital protection logic, automated verification, persistent test evidence and integration between hardware simulation and software tools.

The emphasis is on understanding the engineering workflow, not merely executing a collection of technologies.