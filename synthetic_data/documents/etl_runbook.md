# ETL Runbook

## Customer_Load job
The Customer_Load job should normally complete within 8 minutes. If execution time increases sharply, check for blocking sessions, stale statistics, and query plan regressions. Validate the landing file and row counts before re-running. Do not skip evidence collection.

## Failure triage
When a job fails, record observed facts, hypotheses, and recommendations distinctly. A timeout is not proof of a source file issue unless the file check and logs support it.

## Recommended action
Restart the failed ETL step only after confirming that a new run is safe. Validate row counts and dependency job completion before promoting the next load.
