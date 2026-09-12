# Baseline Query Plan — Observations

## Observation 1 — Parallel Bitmap Heap Scan reads 314,400 rows across 3 workers
Despite an index on date (idx_calendar_date), Postgres still visits 5,296 heap blocks
to fetch actual row data for 104,800 rows per worker across 3 parallel workers.
Total buffer usage for this node: shared hit=12,684 — 87% of all buffer hits in the plan.

## Observation 2 — Two chained Hash Joins rebuild 4,241kB hash table every execution
A Finalize HashAggregate builds a 4,241kB hash table for 10,480 rows (actual time=147..157ms),
which feeds into a Hash Right Join with core.listing, then a Hash Left Join with review_counts.
This entire chain is rebuilt from scratch on every single query execution with no reuse.

## Observation 3 — 1,071kB sort on 10,480 rows to produce just 22 output groups
Postgres sorts all 10,480 joined rows by neighbourhood_id (1,071kB quicksort)
before GroupAggregate collapses them into 22 final rows (276ms total end-to-end).
99.8% of processed rows are intermediate — a materialized view eliminates this entirely.
