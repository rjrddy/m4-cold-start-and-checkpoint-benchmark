from main import measure


def test_real_process_configuration_measurements():
    rows = measure(1)
    assert len(rows) == 3
    assert all(row["p99_ms"] > 0 and row["runs"] == 1 for row in rows)


def test_injected_sleep_appears_in_measurement():
    assert all(row["p99_ms"] >= 20 for row in measure(1, 20))
