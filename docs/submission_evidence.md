# Pull request evidence

Use `starter/d09` → `main` in this fork. The core gate output is:

```text
pass_rate 0.7143  Δ -0.271 CI [-0.500, -0.057] BLOCK
exit 1 — blocked: reply_ledger_consistent, refund_amount_correct, pass_rate
```

`fixed` exits 0. A/A seeds 66,77,88,99,110 give zero delta for every reported v2 metric. Each of the public traps `evaluator_errors_as_nan`, `dropped_failing_rows`, `cherry_picked_seeds`, and `loosened_spec` is blocked (gate exit 1). `lab9.traps` exits 0 because all four are blocked. The `money_movement` slice blocks the public slice regression at 0.85 against a 0.95 floor. The flaky regression is blocked with `pass_hat_5 = 0.5714` (floor 0.80). See `eval_card.md` for run IDs, metric thresholds and limits.

```text
fixed                expect merge got merge ok
honest_refactor      expect merge got merge ok
seeded_regression    expect block got block ok
slice_regression     expect block got block ok
flaky_regression     expect block got block ok
mutation score 3/3 · false alarms 0
```
