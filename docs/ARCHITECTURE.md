# Architecture

The package has three small layers:

1. scanner walks a filesystem and extracts lightweight static signals.
2. report aggregates file-level signals into a JSON-serializable structure.
3. cli validates arguments and writes the report.

The scanner is deliberately local and read-only. It does not use a database,
network client, plugin system, or code executor.
