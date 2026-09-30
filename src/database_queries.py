from database import connect_database

def get_all_test_runs(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            run_id,
            device_id,
            test_id,
            started_at_utc,
            passed,
            error_message
        FROM test_runs;
        """
    )

    return cursor.fetchall()

def get_failed_test_runs(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            run_id,
            device_id,
            test_id,
            started_at_utc,
            error_message
        FROM test_runs
        WHERE passed = 0;
        """
    )

    return cursor.fetchall()

def get_recent_test_runs(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            run_id,
            test_id,
            started_at_utc,
            passed
        FROM test_runs
        ORDER BY started_at_utc DESC;
        """
    )

    return cursor.fetchall()

def get_runs_for_device(
    connection,
    device_id: str,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            run_id,
            test_id,
            started_at_utc,
            passed
        FROM test_runs
        WHERE device_id = ?
        ORDER BY started_at_utc DESC;
        """,
        (
            device_id,
        ),
    )

    return cursor.fetchall()

def get_runs_for_test_case(
    connection,
    test_id: str,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            run_id,
            device_id,
            started_at_utc,
            passed
        FROM test_runs
        WHERE test_id = ?
        ORDER BY started_at_utc DESC;
        """,
        (
            test_id,
        ),
    )

    return cursor.fetchall()

def count_test_runs(
    connection,
) -> int:

    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM test_runs;
        """
    )

    return cursor.fetchone()[0]

def count_runs_by_result(
    connection,
    passed: bool,
) -> int:

    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM test_runs
        WHERE passed = ?;
        """,
        (
            int(passed),
        ),
    )

    return cursor.fetchone()[0]

def calculate_pass_rate(
    connection,
) -> float:

    total_runs = count_test_runs(
        connection
    )

    if total_runs == 0:
        return 0.0

    passed_runs = count_runs_by_result(
        connection,
        True,
    )

    return (
        passed_runs
        / total_runs
        * 100.0
    )

def get_test_history(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            test_runs.run_id,
            test_runs.test_id,
            test_cases.test_name,
            test_runs.started_at_utc,
            test_runs.passed
        FROM test_runs
        JOIN test_cases
            ON test_runs.test_id =
               test_cases.test_id
        ORDER BY
            test_runs.started_at_utc DESC;
        """
    )

    return cursor.fetchall()

def get_complete_test_history(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            test_runs.run_id,
            devices.device_id,
            devices.device_name,
            test_cases.test_id,
            test_cases.test_name,
            test_runs.started_at_utc,
            test_runs.passed,
            test_runs.error_message
        FROM test_runs
        JOIN devices
            ON test_runs.device_id =
               devices.device_id
        JOIN test_cases
            ON test_runs.test_id =
               test_cases.test_id
        ORDER BY
            test_runs.started_at_utc DESC;
        """
    )

    return cursor.fetchall()

def get_fpga_outputs_for_run(
    connection,
    run_id: str,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            timestamp,
            state_code,
            fault_code,
            alarm,
            shutdown
        FROM fpga_outputs
        WHERE run_id = ?
        ORDER BY timestamp;
        """,
        (
            run_id,
        ),
    )

    return cursor.fetchall()

def get_runs_that_entered_fault(
    connection,
) -> list[str]:

    cursor = connection.execute(
        """
        SELECT DISTINCT run_id
        FROM fpga_outputs
        WHERE state_code = 3
        ORDER BY run_id;
        """
    )

    return [
        row[0]
        for row
        in cursor.fetchall()
    ]

def get_fault_events_for_run(
    connection,
    run_id: str,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            fault_type,
            start_timestamp,
            duration
        FROM fault_events
        WHERE run_id = ?
        ORDER BY start_timestamp;
        """,
        (
            run_id,
        ),
    )

    return cursor.fetchall()

def find_simultaneous_faults(
        connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            run_id,
            COUNT(*) AS fault_count
        FROM fault_events
        GROUP BY run_id
        HAVING COUNT(*) > 1;
        """
    )

    return cursor.fetchall()

def count_faults_by_type(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            fault_type,
            COUNT(*) AS event_count
        FROM fault_events
        GROUP BY fault_type
        ORDER BY event_count DESC;
        """
    )

    return cursor.fetchall()

def count_runs_by_test_case(
    connection,
) -> list[tuple]:

    cursor = connection.execute(
        """
        SELECT
            test_cases.test_id,
            test_cases.test_name,
            COUNT(test_runs.run_id)
                AS run_count
        FROM test_cases
        JOIN test_runs
            ON test_cases.test_id =
               test_runs.test_id
        GROUP BY
            test_cases.test_id,
            test_cases.test_name
        ORDER BY run_count DESC;
        """
    )

    return cursor.fetchall()

def get_run_details(
    connection,
    run_id: str,
) -> tuple | None:

    cursor = connection.execute(
        """
        SELECT
            test_runs.run_id,
            devices.device_id,
            devices.device_name,
            test_cases.test_id,
            test_cases.test_name,
            test_cases.description,
            test_runs.started_at_utc,
            test_runs.passed,
            test_runs.error_message
        FROM test_runs
        JOIN devices
            ON test_runs.device_id =
               devices.device_id
        JOIN test_cases
            ON test_runs.test_id =
               test_cases.test_id
        WHERE test_runs.run_id = ?;
        """,
        (
            run_id,
        ),
    )

    return cursor.fetchone()

def print_database_summary(
    connection,
) -> None:

    total = count_test_runs(
        connection
    )

    passed = count_runs_by_result(
        connection,
        True,
    )

    failed = count_runs_by_result(
        connection,
        False,
    )

    pass_rate = calculate_pass_rate(
        connection
    )

    print(
        "VETP DATABASE SUMMARY"
    )

    print(
        "---------------------"
    )

    print(
        f"Total runs: {total}"
    )

    print(
        f"Passed: {passed}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Pass rate: "
        f"{pass_rate:.1f}%"
    )

if __name__ == "__main__":

    connection = connect_database()

    try:
        print_database_summary(connection)

        print("\nALL TEST RUNS")
        print("---------------------")

        runs = get_all_test_runs(connection)

        for run in runs:
            print(dict(run))

        print("\nRUNS FOR PWR-001")
        print("---------------------")

        runs = get_runs_for_device(
            connection,
            "PWR-001",
        )

        for run in runs:
            print(dict(run))

        print("\nRUNS FOR TC-005")
        print("---------------------")

        runs = get_runs_for_test_case(
            connection,
            "TC-005",
        )

        for run in runs:
            print(dict(run))

        print("\nCOMPLETE TEST HISTORY")
        print("---------------------")

        for run in get_complete_test_history(
            connection
        ):
            print(dict(run))

        print("\nRUN DETAILS")
        print("---------------------")

        run = get_run_details(
            connection,
            "RUN-DEMO-001",
        )

        if run is not None:
            print(dict(run))
        else:
            print("Run not found.")

        print("\nFPGA OUTPUTS")
        print("---------------------")

        outputs = get_fpga_outputs_for_run(
            connection,
            "RUN-DEMO-001",
        )

        for output in outputs:
            print(dict(output))

        print("\nFAULT EVENTS")
        print("---------------------")

        faults = get_fault_events_for_run(
            connection,
            "RUN-DEMO-001",
        )

        for fault in faults:
            print(dict(fault))

        print("\nRUNS THAT ENTERED FAULT")
        print("---------------------")

        print(
            get_runs_that_entered_fault(
                connection
            )
        )

        print("\nFAULT COUNTS BY TYPE")
        print("---------------------")

        for result in count_faults_by_type(
            connection
        ):
            print(dict(result))

        print("\nEXECUTIONS BY TEST CASE")
        print("---------------------")

        for result in count_runs_by_test_case(
            connection
        ):
            print(dict(result))

    finally:
        connection.close()