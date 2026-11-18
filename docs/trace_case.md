# Trace case: C-002@11

Trial `seeded_regression C-002@11` (see `reports/eval_seeded_regression.json`): Lab 8's grader fails on status; ledger records 20,000 VND and one refund, while the label requires zero and denied. The reply says 20,000 VND.

The first erroneous event is **3, `model_override`, `{"delay_days": 5}`**: the ticket's claim replaces the database fact returned by event 2 (`investigator`). Event 1 is the handoff and event 2 is the lookup; neither changes that fact. Event 4 quotes 20,000 and event 6 reports the refund, both downstream of the override. This is FM-03.

The `fixed` control for the same claim and seed has no override: event 3 quotes zero, event 4 denies the request, and the ledger remains zero. `src/tests/test_lab9_regression_case.py::test_ticket_override_regression` checks both trajectories and outcomes. The trace establishes the observable override and outcome, but not a model's internal reasoning.
