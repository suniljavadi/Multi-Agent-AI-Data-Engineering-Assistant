# Rollback Procedure

1. Stop the current pipeline or job in the release window.
2. Restore the last known-good package or deployment artifact.
3. Validate downstream dependencies and row counts.
4. Re-enable the downstream consumers after validation.
5. Record the incident and attach evidence to the ticket.

Rollback is only acceptable when the current version has clear evidence of failure or data correctness issues.
