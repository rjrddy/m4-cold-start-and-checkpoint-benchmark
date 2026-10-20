1. Reproducible benchmark of container and process start/restore times across kernels, with a regression gate. Pair with an upstream PR.

2. Result:
   Process configurations measured: 3  
   Process launches measured: 60  
   CRIU restores measured: 0  

   Measured with `make bench`: [raw results](evidence/bench.json), [command output](evidence/checks.log), [environment](evidence/environment.json).

3. Architecture:
```mermaid
flowchart LR
    ThreeProcessConfigs --> WallClockTiming --> SnapshotRead --> RegressionGate
```

4. Run it:
```sh
make setup
make lint test bench
.venv/bin/python src/main.py --gate --inject-ms 500  # expected exit 1
```

5. Decisions and limits: Partial: measurements cover three real Python process configurations on this host, not three kernels, container cold starts, or CRIU restoration. The snapshot case deserializes application state; it is explicitly not process checkpoint restoration. No upstream target-repo PR was fabricated; the required substantive upstream PR remains absent. See evidence/baseline.json and evidence/gate-failure.log for the actual measured slowdown gate. Docker and CRIU are unavailable locally.

6. Next: Run a Linux kernel/configuration matrix with Docker and CRIU, then contribute a substantive benchmark or compatibility fix upstream.
