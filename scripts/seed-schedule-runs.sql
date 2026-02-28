-- Seed schedule_runs with 11 known 28-feb runs (Huddinge 2w expanded).
-- Uses REPLACE so re-running overwrites existing rows with full metrics (efficiency, continuity, etc.).
-- Run: sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-runs.sql

INSERT OR REPLACE INTO schedule_runs (
  id, dataset, batch, algorithm, strategy, hypothesis, status,
  timefold_score, routing_efficiency_pct, unassigned_visits, total_visits, unassigned_pct,
  continuity_avg, continuity_max, continuity_over_target, continuity_target,
  submitted_at
) VALUES
  ('203cf1d6', 'huddinge-2w-expanded', '28-feb', 'continuity-pool', 'Continuity pool (first-run style)', 'Limit caregivers per client via pool.', 'completed', '0hard/-680000medium/-2011536soft', 87.15, 68, 3622, 1.88, 2.5, 6, 0, 11, datetime('now')),
  ('2b36ebdb', 'huddinge-2w-expanded', '28-feb', 'continuity-pool', 'Continuity pool variant', 'Slight change to pool assignment.', 'completed', '0hard/-720000medium/-2008216soft', 87.13, 72, 3622, 1.99, 2.5, 6, 0, 11, datetime('now')),
  ('41ce610c', 'huddinge-2w-expanded', '28-feb', 'manual-pools', 'Manual continuity pools (per-client cross-type)', 'Per-client pool of max 15 caregivers.', 'completed', '0hard/-420000medium/-1796153soft', 89.82, 42, 3622, 1.16, 12.9, 28, 30, 11, datetime('now')),
  ('48b04930', 'huddinge-2w-expanded', '28-feb', 'tighter-pools', 'Tighter continuity pools', 'Smaller pool size to push continuity avg down.', 'completed', '0hard/-260000medium/-1793531soft', 89.86, 26, 3622, 0.72, 13.7, 27, 32, 11, datetime('now')),
  ('5ff7929f', 'huddinge-2w-expanded', '28-feb', 'base-no-continuity', 'Base solve, no continuity constraint', 'Maximize assignment and efficiency first.', 'completed', '0hard/-60000medium/-2515019soft', 86.12, 6, 3622, 0.17, 19.6, 36, 58, 11, datetime('now')),
  ('7c002442', 'huddinge-2w-expanded', '28-feb', 'from-patch-trim', 'from-patch trim-empty (variant)', 'Pin visits and trim empty shifts.', 'completed', '0hard/-1120000medium/-1834162soft', 88.22, 112, 3622, 3.09, 2.3, 4, 0, 11, datetime('now')),
  ('82a338b9', 'huddinge-2w-expanded', '28-feb', 'from-patch-trim', 'from-patch trim-empty shifts', 'Pin assigned visits, trim empty shifts. Best unassigned so far.', 'completed', '0hard/-40000medium/-1773494soft', 90.03, 4, 3622, 0.11, 14.0, 33, 0, 11, datetime('now')),
  ('8a2318b9', 'huddinge-2w-expanded', '28-feb', 'from-patch-trim', 'from-patch trim-empty (variant)', 'Same as 82a338b9 with different pin set.', 'completed', '0hard/-1120000medium/-1871073soft', 88.08, 112, 3622, 3.09, 2.4, 4, 0, 11, datetime('now')),
  ('a9664f39', 'huddinge-2w-expanded', '28-feb', 'area-firstrun', 'Area / first-run pool', 'Geographic or first-run grouping.', 'completed', '0hard/-660000medium/-2474475soft', 84.24, 66, 3622, 1.82, 2.7, 6, 0, 11, datetime('now')),
  ('b69e582b', 'huddinge-2w-expanded', '28-feb', 'from-patch-trim', 'from-patch trim-empty (variant)', 'Same family as 82a338b9; good efficiency.', 'completed', '0hard/-40000medium/-1772308soft', 90.03, 4, 3622, 0.11, 14.2, 33, 33, 11, datetime('now')),
  ('b8e58647', 'huddinge-2w-expanded', '28-feb', 'continuity-pool', 'Continuity pool', 'Pool-based constraint to cap distinct caregivers.', 'completed', '0hard/-640000medium/-2029805soft', 87.02, 64, 3622, 1.77, 2.5, 6, 0, 11, datetime('now'));
