from database import (
    connect_database,
    create_tables,
)

from database_integration import save_completed_run

from fpga_runner import (
    run_engineering_test,
    CAMPAIGN_LOG_DIR,
)

from fpga_test_cases import build_engineering_test_cases

from test_logging import (
    build_campaign_summary,
    save_campaign_summary,
)


def run_persistent_campaign(database_path=None):

    cases = build_engineering_test_cases()

    logs = []

    connection = (
        connect_database()
        if database_path is None
        else connect_database(database_path)
    )

    try:

        create_tables(connection)

        for case in cases:


            log = run_engineering_test(case)

            try:
                save_completed_run(
                    connection,
                    case,
                    log,
                )

                connection.commit()

            except Exception:
                connection.rollback()

                print(
                    f"SQLite save failed for {log.run_id}; "
                    "JSON log remains available."
                )

                raise

            logs.append(log)

            print(
                f"Saved SQLite run: {log.run_id} | "
                f"{'PASS' if log.passed else 'FAIL'}"
            )

        summary = build_campaign_summary(logs)

        path = save_campaign_summary(
            summary,
            CAMPAIGN_LOG_DIR,
        )

        print(
            f"Campaign: {summary.total_tests} total, "
            f"{summary.passed_tests} passed, "
            f"{summary.failed_tests} failed"
        )

        print(
            f"JSON campaign summary: {path}"
        )

        return summary

    finally:
        connection.close()


if __name__ == "__main__":
    run_persistent_campaign()