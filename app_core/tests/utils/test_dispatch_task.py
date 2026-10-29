import logging

import pytest

from utils.dispatch_task import dispatch_task


def test_dispatch_task_runs_the_action() -> None:
    calls: list[str] = []

    dispatch_task(action=lambda: calls.append("ran"), description="example task")

    assert calls == ["ran"]


def test_dispatch_task_swallows_an_exception_instead_of_letting_it_propagate(
    caplog: pytest.LogCaptureFixture,
) -> None:
    def failing_action() -> None:
        raise RuntimeError("broker is unreachable")

    with caplog.at_level(logging.WARNING):
        dispatch_task(action=failing_action, description="send_email_verification_email")

    #   The whole point of this helper: a dispatch failure (e.g. a broker outage)
    #   must never turn into a failed HTTP response for the caller.
    assert "send_email_verification_email" in caplog.text


def test_dispatch_task_logs_the_exception_info_on_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    def failing_action() -> None:
        raise RuntimeError("broker is unreachable")

    with caplog.at_level(logging.WARNING):
        dispatch_task(action=failing_action, description="example task")

    assert "broker is unreachable" in caplog.text
