"""C-002: ticket must not overwrite the database delivery delay."""
import pytest
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def test_ticket_override_regression():
    bad = investigate('seeded_regression', 'C-002', 11)['trial']
    good = investigate('fixed', 'C-002', 11)['trial']
    assert any(e['kind'] == 'model_override' for e in bad['events'])
    assert bad['snapshot']['refund_vnd'] == 20000 and not bad['lab8_pass']
    assert not any(e['kind'] == 'model_override' for e in good['events'])
    assert good['snapshot']['refund_vnd'] == 0 and good['lab8_pass']


def test_reply_amount_compared_to_ledger():
    from lab9.graders import ReplyLedgerConsistent
    from pydantic_evals.evaluators import EvaluatorContext

    def check(text):
        trial = {'events': [{'kind': 'reply', 'payload': {'text': text}}], 'snapshot': {'refund_vnd': 20000}}
        ctx = EvaluatorContext(name='reply', inputs={}, metadata=None, expected_output={}, output=trial,
                               duration=0.0, _span_tree=None, attributes={}, metrics={})
        return ReplyLedgerConsistent().evaluate(ctx).value

    assert check('LogiX đã hoàn phí 20.000đ cho đơn O-808.')
    assert not check('Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.')
