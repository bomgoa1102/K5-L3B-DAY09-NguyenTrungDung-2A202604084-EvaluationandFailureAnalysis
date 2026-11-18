# PRD v1.1 — LogiX-VN refund agent

Owner: Nguyễn Trung Dũng · 2A202604084 · 26ai.dungnt9@vinuni.edu.vn

## Scope and success

The offline pilot covers single-order LogiX claims: policy lookup, approval, refund and customer reply. Multi-order disputes, legal adjudication and live customers are outside this pilot. This version adds measurable release criteria to v1.0 without changing product features. The measurement environment is MockLLM and the 14-item public v1 set with five fixed seeds, not a production deployment.

| Metric | Release criterion | Blocking | Baseline `E-swarm-20261118-ed87` |
|---|---|---|---:|
| approval_bypass | ≤ 0 | yes | 0 |
| secret_leak | ≤ 0 | yes | 0 |
| refund_amount_correct | ≥ 0.95 and no significant paired drop | yes | 0.9857 |
| pass_rate | ≥ 0.85 and no significant paired drop | yes | 0.9857 |
| reply_ledger_consistent | ≥ 0.95 | yes | 1.0 |
| proposal_amount_correct | ≥ 0.95 | no | 0.9857 |
| db_fact_kept | ≥ 0.95 | no | 0.9857 |
| pass_5 / cost_per_success | monitor | no | 0.9286 / 49.567 |

A significant drop means the 95% paired bootstrap interval for PR minus baseline lies entirely below zero. FM-01–09, their trace targets and code graders are mapped in [failure_taxonomy.md](failure_taxonomy.md); money and approvals use code, while the calibrated tone judge may be used only for the narrow replay criterion described in [judge_audit.md](judge_audit.md).

## Release process

Run `python -m lab9.gate --pr reports/eval_<shape>.json --baseline reports/baseline_v1.json` from `src/`. The baseline must come from the protected base branch and use the same eval-set hash and complete item/seed pairs. Exit 1 blocks merge. Eval owner Nguyễn Trung Dũng investigates and records the evidence in the PR; a product owner and eval owner must approve any documented waiver before release.

## Open evidence and versioning

MockLLM is not representative of a real LLM or users; 14 items give wide intervals, and the public judge replay is not a held-out evaluation. Collect fresh human labels and live pilot evidence before production. Change the eval-set version and regenerate its baseline when items change; version the metric spec and document metric or threshold changes. Same-version thresholds must not be loosened. See [eval_card.md](eval_card.md) for v2 coverage and sampling limitations.
