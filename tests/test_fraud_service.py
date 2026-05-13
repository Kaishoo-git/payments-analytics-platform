import pytest

from app.services.fraud_service import FraudService


def test_low_amount_transaction_should_approve():
    service = FraudService()

    score, decision = service.evaluate(50)

    assert decision == "APPROVE"
    assert 0 <= score <= 1


def test_high_amount_transaction_should_decline():
    service = FraudService()

    score, decision = service.evaluate(6000)

    assert decision == "DECLINE"
    assert score >= 0.8


def test_boundary_transaction_amount():
    service = FraudService()
    score1, decision1 = service.evaluate(4999)
    score3, decision3 = service.evaluate(5001)

    assert decision1 != decision3


def test_zero_amount_transaction():
    service = FraudService()

    score, decision = service.evaluate(0)

    assert decision == "APPROVE"
    assert score == 0


@pytest.mark.parametrize(
    "amount, expected_decision",
    [
        (10, "APPROVE"),
        (100, "APPROVE"),
        (2000, "REVIEW"),
        (5000, "REVIEW"),
        (7000, "DECLINE"),
    ],
)
def test_fraud_decision_matrix(amount, expected_decision):
    service = FraudService()

    _, decision = service.evaluate(amount)

    assert decision == expected_decision