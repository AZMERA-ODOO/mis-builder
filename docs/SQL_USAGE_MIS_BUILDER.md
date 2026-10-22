# MIS Builder SQL Usage

MIS Builder is maintained in this repository and is not part of the beverage
core SQL boundary. Direct cursor SQL is permitted only for the documented
model-initialization exception below.

<!-- sql-guardrail-allowlist:start -->

- `mis_builder/models/mis_report_instance_annotation.py` — idempotent composite
  PostgreSQL index for annotation lookups during model initialization.

<!-- sql-guardrail-allowlist:end -->

## Exception contract

The ORM has no idempotent API for declaring this composite index. The index
protects lookup performance for period, KPI, and sub-KPI annotation searches.
`CREATE INDEX IF NOT EXISTS` makes repeated installation and initialization
safe. The annotation test suite verifies the index contract; the repository
SQL guardrail check must be run for this fork before release.

This exception does not authorize cursor SQL in reporting or business logic.
