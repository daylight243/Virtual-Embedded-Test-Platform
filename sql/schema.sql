CREATE TABLE IF NOT EXISTS devices(
    device_id TEXT PRIMARY KEY,
    device_name TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_cases (
    test_id TEXT PRIMARY KEY,

    test_name TEXT NOT NULL,

    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_runs (
    run_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    test_id TEXT NOT NULL,
    started_at_utc TEXT NOT NULL,
    passed INTEGER NOT NULL,
    error_message TEXT,


    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    FOREIGN KEY (test_id) REFERENCES test_cases(test_id),
    
    CHECK (passed IN (0, 1))
);

CREATE TABLE IF NOT EXISTS fpga_outputs (
    output_id INTEGER PRIMARY KEY AUTOINCREMENT,

    run_id TEXT NOT NULL,

    timestamp INTEGER NOT NULL,

    state_code INTEGER NOT NULL,

    fault_code INTEGER NOT NULL,

    alarm INTEGER NOT NULL,

    shutdown INTEGER NOT NULL,

    FOREIGN KEY (run_id)
        REFERENCES test_runs(run_id),

    CHECK (alarm IN (0, 1)),

    CHECK (shutdown IN (0, 1))
);

CREATE TABLE IF NOT EXISTS fault_events (
    fault_event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    run_id TEXT NOT NULL,

    fault_type TEXT NOT NULL,

    start_timestamp INTEGER NOT NULL,

    duration INTEGER NOT NULL,

    FOREIGN KEY (run_id)
        REFERENCES test_runs(run_id),

    CHECK (start_timestamp >= 0),

    CHECK (duration > 0)
);