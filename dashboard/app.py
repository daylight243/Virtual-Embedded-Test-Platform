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

from dashboard_logic import (
    state_name,
    fault_name,
    verification_name,
    find_state_transitions,
    find_fault_transitions,
)


def get_report_path(
    run_id: str,
) -> Path:

    return (
        REPORTS_DIR
        / f"test_{run_id}.md"
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


st.sidebar.title(
    "VETP"
)

st.sidebar.caption(
    "Engineering Workbench"
)

page = st.sidebar.radio(
    "Workspace",
    (
        "Overview",
        "Test History",
        "Run Inspector",
        "Analysis",
    ),
)

st.sidebar.divider()

st.sidebar.caption(
    "Version 1 · SQLite"
)

try:
    connection = connect_database()

except Exception as exc:
    st.error(
        "Unable to open the VETP "
        "SQLite database."
    )

    st.exception(exc)

    st.stop()

def render_overview(connection):
    st.title(
    "Virtual Embedded Test Platform"
    )

    st.caption(
    "Protection Controller · "
    "Engineering Workbench"
    )

    st.subheader(
    "Test System Overview"
    )

    total_runs = count_test_runs(
    connection
    )

    passed_runs = count_runs_by_result(
        connection,
        True,
    )

    failed_runs = count_runs_by_result(
        connection,
        False,
    )

    pass_rate = calculate_pass_rate(
        connection
    )

    history = get_complete_test_history(
    connection
    )

    if history:
        latest_run = history[0]

        st.caption(
            "Latest stored test: "
            f"{latest_run['started_at_utc']}"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Test Runs",
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


    with col4:

        st.metric(
            "Pass Rate",
            f"{pass_rate:.1f}%",
        )
    if total_runs == 0:

        st.info(
            "No test history is stored yet."
        )

    elif failed_runs == 0:

        st.success(
            "Stored verification history "
            "contains no failed runs."
        )

    else:

        st.warning(
            f"{failed_runs} failed verification "
            f"run(s) require review."
        )

    recent_runs = history[:5]
    recent_rows = []

    for run in recent_runs:

        recent_rows.append(
            {
                "Test":
                    run["test_id"],

                "Name":
                    run["test_name"],

                "Started":
                    run["started_at_utc"],

                "Result":
                    (
                        "PASS"
                        if run["passed"]
                        else "FAIL"
                    ),
            }
        )

    st.subheader(
    "Recent Activity"
    )

    st.dataframe(
        recent_rows,
        use_container_width=True,
        hide_index=True,
    )   

    result_data = {
    "Result": [
        "PASS",
        "FAIL",
    ],

    "Runs": [
        passed_runs,
        failed_runs,
    ],
    }

    st.subheader(
    "Verification Results"
    )

    st.bar_chart(
        result_data,
        x="Result",
        y="Runs",
    )
    
def render_test_history(connection):
    
    st.header(
        "Test History"
    )

    st.caption(
        "Search and inspect persistent "
        "engineering test records."
    )

    history = get_complete_test_history(
    connection
    )

    if not history:

        st.info(
            "No test runs are stored yet."
        )

        return

    test_ids = sorted(
    {
        row["test_id"]
        for row in history
    }
    )

    selected_test = st.selectbox(
        "Test Case",
        ["All"] + test_ids,
    )

    selected_result = st.selectbox(
    "Verification Result",
    (
        "All",
        "PASS",
        "FAIL",
    ),
    )

    device_ids = sorted(
    {
        row["device_id"]
        for row in history
    }
    )

    selected_device = st.selectbox(
        "Device",
        ["All"] + device_ids,
    )

    filtered = list(history)

    if selected_test != "All":

        filtered = [
            row
            for row in filtered
            if row["test_id"]
            == selected_test
        ]

    if selected_device != "All":

        filtered = [
            row
            for row in filtered
            if row["device_id"]
            == selected_device
        ]

    if selected_result == "PASS":

        filtered = [
            row
            for row in filtered
            if bool(row["passed"])
        ]

    elif selected_result == "FAIL":

        filtered = [
            row
            for row in filtered
            if not bool(row["passed"])
        ]

    if not filtered:
        st.info(
            "No test runs match "
            "the selected filters."
        )

    else:
        history_rows = [
            {
                "Run ID":
                    row["run_id"],

                "Test":
                    row["test_id"],

                "Test Name":
                    row["test_name"],

                "Device":
                    row["device_id"],

                "Started":
                    row["started_at_utc"],

                "Result":
                    verification_name(
                        row["passed"]
                    ),
            }
            for row in filtered
        ]

        st.dataframe(
            history_rows,
            use_container_width=True,
            hide_index=True,
        )

def render_run_inspector(connection):
    st.header("Run Inspector")

    history = get_complete_test_history(
        connection
    )

    if not history:
        st.info(
            "No test runs are stored yet. "
            "Run an engineering test campaign "
            "to populate the VETP database."
        )
        return


    run_lookup = {}

    for run in history:

        label = (
            f"{run['test_id']} · "
            f"{run['test_name']} · "
            f"{verification_name(run['passed'])} · "
            f"{run['started_at_utc']}"
        )

        run_lookup[label] = (
            run["run_id"]
        )

    selected_label = st.selectbox(
    "Select Test Run",
    list(run_lookup.keys()),
    )

    selected_run_id = (
        run_lookup[selected_label]
    )

    run_details = get_run_details(
    connection,
    selected_run_id,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Test",
            run_details["test_id"],
        )


    with col2:

        st.metric(
            "Device",
            run_details["device_id"],
        )


    with col3:

        st.metric(
            "Result",
            verification_name(
                run_details["passed"]
            ),
        )


    with col4:

        st.metric(
            "Started",
            run_details[
                "started_at_utc"
            ],
        )

    st.subheader(
    run_details["test_name"]
    )

    st.write(
        run_details["description"]
    )

    outputs = get_fpga_outputs_for_run(
    connection,
    selected_run_id,
    )

    timeline = []

    for output in outputs:

        timeline.append(
            {
                "Time":
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
                    (
                        "ON"
                        if output["alarm"]
                        else "OFF"
                    ),

                "Shutdown":
                    (
                        "ON"
                        if output["shutdown"]
                        else "OFF"
                    ),
            }
        )
    st.subheader(
    "FPGA Timeline"
    )

    if not timeline:

        st.warning(
            "No FPGA output samples "
            "were recorded for this run."
        )

    else:

        st.dataframe(
            timeline,
            use_container_width=True,
            hide_index=True,
        )

    transitions = find_state_transitions(
    outputs
    )

    st.subheader(
    "State Transitions"
    )

    st.dataframe(
        transitions,
        use_container_width=True,
        hide_index=True,
    )

    fault_transitions = find_fault_transitions(
        outputs
    )

    st.subheader(
        "Fault-Code Transitions"
    )

    if not fault_transitions:
        st.info(
            "No FPGA fault-code samples "
            "were recorded for this run."
        )
    else:
        st.dataframe(
            fault_transitions,
            use_container_width=True,
            hide_index=True,
        )

    fault_events = (
    get_fault_events_for_run(
        connection,
        selected_run_id,
    )
    )

    st.subheader(
    "Injected Fault Stimuli"
    )
    if not fault_events:
        st.info(
        "No recorded fault injections "
        "for this run."
        ) 

    else:
        st.dataframe(
            [
                {
                    "Fault":
                        event["fault_type"],

                    "Start":
                        event[
                            "start_timestamp"
                        ],

                    "Duration":
                        event["duration"],
                }
                for event in fault_events
            ],
            use_container_width=True,
            hide_index=True,
        ) 

    report_path = get_report_path(
    selected_run_id
    )
    if report_path.exists():
        report_text = (
            report_path.read_text(
                encoding="utf-8"
            )
        )
        st.download_button(
        label="Download Engineering Report",
        data=report_text,
        file_name=report_path.name,
        mime="text/markdown",
        )

    else:
        st.caption(
            "No generated engineering report "
            "was found for this run."
        )



def render_analysis(connection):
        st.header(
            "Engineering Analysis"
        )

        st.caption(
            "Aggregate views of stored "
            "VETP test history."
        )
        test_counts = count_runs_by_test_case(
        connection
        )

        test_count_rows = [
        {
            "Test ID":
                row["test_id"],

            "Test Name":
                row["test_name"],

            "Executions":
                row["run_count"],
        }
        for row in test_counts
        ]

        st.subheader(
            "Test Execution Counts"
        )

        st.dataframe(
            test_count_rows,
            use_container_width=True,
            hide_index=True,
        )

        fault_counts = count_faults_by_type(
        connection
        )
        fault_rows = [
        {
            "Fault Type":
                row["fault_type"],

            "Injected Events":
                row["event_count"],
        }
        for row in fault_counts
        ]

        st.subheader(
        "Injected Fault Counts"
        )

        st.dataframe(
            fault_rows,
            use_container_width=True,
            hide_index=True,
        )

        failures = get_failed_test_runs(
                connection
        )

        st.subheader(
            "Recent Verification Failures"
        )

        if not failures:
            st.success(
                "No failed verification runs "
                "are currently stored."
            )

        else:
            failure_rows = [
                {
                    "Run ID":
                        row["run_id"],

                    "Test":
                        row["test_id"],

                    "Started":
                        row["started_at_utc"],

                    "Error":
                        row["error_message"]
                        or "",
                }
                for row in failures[:10]
            ]

            st.dataframe(
                failure_rows,
                use_container_width=True,
                hide_index=True,
            )
        st.subheader(
        "Electrical Measurement Trends"
        )

        st.info(
            "Analog measurement history is "
            "not yet persisted in the Version 1 "
            "SQLite model. Trend plots will be "
            "enabled when genuine measurement "
            "samples are connected to the "
            "persistent test pipeline."
        )

if page == "Overview":
    
    render_overview(
        connection
    )
    

elif page == "Test History":
    
    render_test_history(
        connection
    )

elif page == "Run Inspector":
    
    render_run_inspector(
            connection
        )

elif page == "Analysis":
    
    render_analysis(
            connection
        )

if st.sidebar.button(
    "Refresh Data"
):
    st.rerun()

connection.close()





    



    


