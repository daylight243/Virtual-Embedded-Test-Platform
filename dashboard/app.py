from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR),
    )

REPORTS_DIR = (
    PROJECT_ROOT
    / "build"
    / "reports"
)

from database import connect_database

from database_queries import (
    count_test_runs,
    count_runs_by_result,
    calculate_pass_rate,
    get_complete_test_history,
    get_failed_test_runs,
    get_fpga_outputs_for_run,
    get_fault_events_for_run,
    count_faults_by_type,
    count_runs_by_test_case,
    get_run_details,
)


STATE_NAMES = {
    0: "IDLE",
    1: "STARTUP",
    2: "RUNNING",
    3: "FAULT",
    4: "RECOVERY",
}


FAULT_NAMES = {
    0: "NONE",
    1: "UV",
    2: "OV",
    3: "OC",
    4: "OT",
}

def state_name(
    state_code: int,
) -> str:

    return STATE_NAMES.get(
        state_code,
        f"UNKNOWN ({state_code})",
    )

def fault_name(
    fault_code: int,
) -> str:

    return FAULT_NAMES.get(
        fault_code,
        f"UNKNOWN ({fault_code})",
    )

st.set_page_config(
    page_title="VETP Dashboard",
    page_icon="⚙️",
    layout="wide",
)


st.title(
    "Virtual Embedded Test Platform"
)

st.caption(
    "Builder Edition — Version 1"
)

st.write(
    "Engineering dashboard is running."
)


page = st.sidebar.radio(
    "Navigate",
    (
        "Overview",
        "Test History",
        "Run Inspector",
        "Analysis",
    ),
)

connection = connect_database()

if page == "Overview":
    st.header("Overview")
    
    total_runs = count_test_runs(
    connection
    )
    st.metric(
    "Total Test Runs",
    total_runs,
    )
    passed_runs = count_runs_by_result(
    connection,
    True,
    )
    failed_runs = count_runs_by_result(
    connection,
    False,
    )
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Runs",
            total_runs,
        )

    with col2:
        st.metric(
            "Passed",
            passed_runs,
        )

    with col3:
        st.metric(
            "Failed",
            failed_runs,
        )

    pass_rate = calculate_pass_rate(
    connection
    )
    st.metric(
    "Pass Rate",
    f"{pass_rate:.1f}%",
    )
    history = get_complete_test_history(
    connection
    )
    recent_runs = history[:5]
    for run in recent_runs:

        result = (
            "PASS"
            if run["passed"]
            else "FAIL"
        )

        st.write(
            f"{run['test_id']} — "
            f"{run['test_name']} — "
            f"{result}"
        )

    

elif page == "Test History":
    st.header("Test History")
    history = get_complete_test_history(
    connection
    )
    history_rows = [
    dict(row)
    for row in history
    ]
    st.dataframe(
    history_rows,
    use_container_width=True,
    )
    test_ids = sorted(
    {
        row["test_id"]
        for row in history
    }
    )
    selected_test = st.selectbox(
    "Filter by Test Case",
    ["All"] + test_ids,
    )
    if selected_test == "All":

        filtered_history = history

    else:

        filtered_history = [
            row
            for row in history
            if row["test_id"]
            == selected_test
        ]

    st.dataframe(
    [
        dict(row)
        for row in filtered_history
    ],
    use_container_width=True,
    )

elif page == "Run Inspector":
    st.header("Run Inspector")
    history = get_complete_test_history(
    connection
    )
    run_ids = [
    row["run_id"]
    for row in history
    ]
    if not run_ids:

        st.info(
            "No test runs are stored yet."
        )

    else:

        selected_run_id = st.selectbox(
            "Select Run",
            run_ids,
        )

        run_details = get_run_details(
        connection,
        selected_run_id,
        )

        if run_details is None:

            st.error(
                "The selected run could not be found."
            )

        else:

            st.subheader(
                run_details["test_name"]
            )

            st.write(
                f"Run ID: "
                f"{run_details['run_id']}"
            )

            st.write(
                f"Device: "
                f"{run_details['device_name']}"
            )

            st.write(
                f"Test ID: "
                f"{run_details['test_id']}"
            )

            st.write(
                f"Started: "
                f"{run_details['started_at_utc']}"
            )
        if run_details["passed"]:

            st.success(
                "Engineering Verification: PASS"
            )

        else:

            st.error(
                "Engineering Verification: FAIL"
            )

    outputs = get_fpga_outputs_for_run(
    connection,
    selected_run_id,
    )

    output_rows = []

    for output in outputs:

        output_rows.append(
            {
                "Timestamp":
                    output["timestamp"],

                "State":
                    state_name(
                        output["state_code"]
                    ),

                "State Code":
                    output["state_code"],

                "Fault":
                    fault_name(
                        output["fault_code"]
                    ),

                "Fault Code":
                    output["fault_code"],

                "Alarm":
                    bool(output["alarm"]),

                "Shutdown":
                    bool(output["shutdown"]),
            }
        )
    st.subheader(
    "FPGA Output Timeline"
    )

    st.dataframe(
        output_rows,
        use_container_width=True,
    )

    fault_events = get_fault_events_for_run(
    connection,
    selected_run_id,
    )

    st.subheader(
    "Fault Injection Events"
    )

    if not fault_events:

        st.info(
            "No recorded fault injections "
            "for this run."
        )
    else:
        st.dataframe(
        [
            dict(event)
            for event in fault_events
        ],
        use_container_width=True,
        )

    report_path = (
    REPORTS_DIR
    / f"test_{selected_run_id}.md"
    )

    if report_path.exists():
        st.success(
        "Engineering report available."
        )

elif page == "Analysis":
    st.header("Analysis")
    st.header(
    "Engineering Analysis"
    )
    fault_counts = count_faults_by_type(
    connection
    )
    st.subheader(
    "Recorded Fault Events"
    )
    fault_count_rows = [
    {
        "Fault Type": row["fault_type"],
        "Event Count": row["event_count"],
    }
    for row in fault_counts
    ]
    st.dataframe(
    fault_count_rows,
    use_container_width=True,
    )
    test_counts = count_runs_by_test_case(
    connection
    )
    st.subheader(
    "Executions by Test Case"
    )

    st.dataframe(
        [
            {
                "Test ID": row["test_id"],
                "Test Name": row["test_name"],
                "Runs": row["run_count"],
            }
            for row in test_counts
        ],
        use_container_width=True,
    )

    failed_runs = get_failed_test_runs(
    connection
    )
    st.subheader(
    "Recent Verification Failures"
    )
    if not failed_runs:

        st.success(
            "No verification failures "
            "are currently stored."
        )
    else:       
        st.dataframe(
        [
            dict(row)
            for row in failed_runs[:10]
        ],
        use_container_width=True,
        )

    st.subheader(
    "Measurement Trends"
    )

    st.info(
        "Measurement trend analysis will "
        "be enabled when real electrical "
        "measurement samples are connected "
        "to the persistent test pipeline."
    )




if st.sidebar.button(
    "Refresh Data"
):
    st.rerun()

connection.close()



