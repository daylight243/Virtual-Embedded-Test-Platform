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
    load_cloud_config,
    publish_run_summary,
)

from cloud_workflow import publish_completed_campaign, publication_status

from cloud_reciepts import save_publication_receipt

def run_persistent_campaign(
    database_path=None,
):

    # --------------------------------------------------
    # Build the engineering test cases
    # --------------------------------------------------

    cases = build_engineering_test_cases()

    logs = []

    # -----------------------------------------------------
    # Load cloud configuration
    # -----------------------------------------------------

    cloud_config = load_cloud_config()

    print(
        f"Cloud mode: {cloud_config.mode}"
    )


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

            # ---------------------------------------------
            # Publish selected engineering results
            # ---------------------------------------------

            try:

                cloud_summary = (
                    build_cloud_run_summary(
                        test_log=log,
                        device_id=DEVICE_ID,
                    )
                )

                publish_result = (
                    publish_run_summary(
                        cloud_summary,
                        cloud_config,
                    )
                )

                print(
                    "Cloud publication:"
                )

                print(
                    f"  Run: "
                    f"{publish_result.run_id}"
                )

                print(
                    f"  Success: "
                    f"{publish_result.success}"
                )

                print(
                    f"  Destination: "
                    f"{publish_result.destination}"
                )

                print(
                    f"  Status: "
                    f"{publish_result.status_code}"
                )

                print(
                    f"  Message: "
                    f"{publish_result.message}"
                )

            except Exception as error:

                print(
                    "Cloud publication failed for "
                    f"{log.run_id}: {error}"
                )

                print(
                    "Engineering verification "
                    "result remains unchanged."
                )
            # ---------------------------------------------
            # Preserve run in campaign collection
            # ---------------------------------------------
            logs.append(
                log
            )

            print(
                f"Saved SQLite run: {log.run_id} | "
                f"{'PASS' if log.passed else 'FAIL'}"
            )
        # -------------------------------------------------
        # Build the campaign summary
        # -------------------------------------------------
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
        
        completed_logs = tuple(logs)

        workflow_result = publish_completed_campaign(
            test_logs=completed_logs,
            device_id=DEVICE_ID,
            connection=connection,
            config=cloud_config,
        )

        receipt_path = save_publication_receipt(
            workflow_result
        )

        print()
        print("Final campaign cloud workflow:")

        print(
            "  Campaign:",
            workflow_result.campaign_id
        )

        print(
            "  Engineering PASS:",
            workflow_result.engineering_passed
        )

        print(
            "  Publication status:",
            publication_status(workflow_result)
        )

        print(
            "  Publication message:",
            workflow_result.message
        )

        print(
            "  Artifact:",
            workflow_result.artifact_path
        )

        print(
            "  Receipt:",
            receipt_path
        )

        return campaign_summary

    finally:
        connection.close()



# =========================================================
# Program entry point
# =========================================================
if __name__ == "__main__":

    run_persistent_campaign()

