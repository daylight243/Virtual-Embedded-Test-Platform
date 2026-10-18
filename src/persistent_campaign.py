from database import (
    connect_database,
    create_tables,
)

from database_integration import (
    save_completed_run,
    DEVICE_ID,
)

from database_queries import (
    get_fault_events_for_run,
)

from fpga_runner import (
    run_engineering_test,
    CAMPAIGN_LOG_DIR,
)

from fpga_test_cases import (
    build_engineering_test_cases,
)

from report_generator import (
    build_test_report,
    save_test_report,
    build_campaign_report,
    save_campaign_report,
)

from test_logging import (
    build_campaign_summary,
    save_campaign_summary,
)

from cloud_integration import (
    build_cloud_run_summary,
    publish_run_summary_locally,
)



def run_persistent_campaign(
    database_path=None,
):

    # --------------------------------------------------
    # Build the engineering test cases
    # --------------------------------------------------

    cases = build_engineering_test_cases()

    logs = []

    # --------------------------------------------------
    # Connect to SQLite
    # --------------------------------------------------

    connection = (
        connect_database()
        if database_path is None
        else connect_database(database_path)
    )

    try:

        # --------------------------------------------------
        # Individual test transactions created
        # before beginning the database tables. 
        # 
        # --------------------------------------------------

        create_tables(connection)

        # --------------------------------------------------
        # Run each engineering test
        # --------------------------------------------------

        for case in cases:

            log = run_engineering_test(
                case
            )

            # --------------------------------------------------
            # Save SQLite evidence
            # --------------------------------------------------

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


            # --------------------------------------------------
            # Prepare the cloud-ready payload locally
            # --------------------------------------------------
            cloud_summary = build_cloud_run_summary(
                test_log=log,
                device_id=DEVICE_ID,
            )

            publish_result = (
                publish_run_summary_locally(
                    cloud_summary
                )
            )

            print(
                f"Cloud publication: "
                f"{publish_result.message}"
            )

            print(
                f"Destination: "
                f"{publish_result.destination}"
            )
            # --------------------------------------------------
            # Generate the individual Markdown report
            # after successful SQLite persistence.
            # --------------------------------------------------

            try:

                fault_events = get_fault_events_for_run(
                    connection,
                    log.run_id,
                )

                report_text = build_test_report(
                    log,
                    fault_events,
                )

                report_path = save_test_report(
                    log,
                    report_text,
                )

                print(
                    f"Report: {report_path}"
                )

            except Exception as error:

                print(
                    f"Report generation failed for "
                    f"{log.run_id}: {error}"
                )


            logs.append(
                log
            )

            print(
                f"Saved SQLite run: {log.run_id} | "
                f"{'PASS' if log.passed else 'FAIL'}"
            )

        campaign_summary = build_campaign_summary(
            logs
        )

        summary_path = save_campaign_summary(
            campaign_summary,
            CAMPAIGN_LOG_DIR,
        )

        print(
            f"Campaign: "
            f"{campaign_summary.total_tests} total, "
            f"{campaign_summary.passed_tests} passed, "
            f"{campaign_summary.failed_tests} failed"
        )

        print(
            f"JSON campaign summary: {summary_path}"
        )

        # --------------------------------------------------
        # Generate the Markdown campaign report
        # --------------------------------------------------

        try:

            campaign_report = build_campaign_report(
                campaign_summary
            )

            campaign_path = save_campaign_report(
                campaign_summary,
                campaign_report,
            )

            print(
                f"Campaign report: {campaign_path}"
            )

        except Exception as error:

            print(
                f"Campaign report generation failed: "
                f"{error}"
            )

        return campaign_summary

    finally:
        connection.close()


if __name__ == "__main__":

    run_persistent_campaign()