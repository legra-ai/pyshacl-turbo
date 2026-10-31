"""The shared worker owns capture cleanup across every measured phase."""

import contextlib
import io
import sys
import warnings
from types import SimpleNamespace

import pytest
from test_literal_fanout_benchmark import load, mock_worker_rss

JOB = {"operation": "owlrl", "backend": "reference", "nodes": 32, "fixture": "literal-reflexivity"}


def capture_state():
    return sys.stdout, sys.stderr, warnings.filters, list(warnings.filters), warnings.showwarning


def assert_restored(before):
    assert sys.stdout is before[0] and sys.stderr is before[1]
    assert warnings.filters is before[2] and warnings.filters == before[3]
    assert warnings.showwarning is before[4]


def test_warning_encoding_is_after_the_timer_not_inside_the_public_call(monkeypatch):
    import owlrl

    suite = load("companions")
    mock_worker_rss(monkeypatch, suite)
    timed, invoking = [False], [False]
    encoded = []

    class Signal(UserWarning):
        def __str__(self):
            encoded.append((timed[0], invoking[0]))
            return "observable warning"

    class Closure:
        def __init__(self, _):
            pass

        def expand(self, source):
            invoking[0] = True
            warnings.warn(Signal(), stacklevel=1)
            invoking[0] = False

    ticks = iter([10, 20, 30, 40])

    def clock():
        timed[0] = not timed[0]
        return next(ticks)

    monkeypatch.setattr(owlrl, "DeductiveClosure", Closure)
    monkeypatch.setattr(suite.time, "perf_counter_ns", clock)
    result = suite.worker(JOB, 1, "time")
    assert result["samples_ns"] == [10]
    assert any(not call for _, call in encoded)
    assert all(not time_active for time_active, call in encoded if not call)


def test_end_prepare_capture_closes_idempotently_before_effect_encoding():
    suite = load("companions")
    before = capture_state()
    call = None
    try:
        call, observe = suite.prepare(JOB)
        assert sys.stdout is not before[0] and sys.stderr is not before[1]
        value = call()
        result = observe(value)
        assert_restored(before)
        call.close()
        call.close()
        assert_restored(before)
        assert result["public_effects"]["returned_none"]
    finally:
        if call is not None and hasattr(call, "close"):
            call.close()


@pytest.mark.parametrize(
    "phase", ["setup_rss", "first_clock", "second_clock", "post_rss", "invoke", "observe"]
)
def test_worker_finally_cleans_captured_owner_on_every_baseexception(monkeypatch, phase):
    suite = load("companions")
    resource = mock_worker_rss(monkeypatch, suite)
    before = capture_state()

    class Failure(BaseException):
        pass

    failure = Failure("exact", phase)

    class Owner:
        def __init__(self):
            self.stack = contextlib.ExitStack()
            self.stack.enter_context(warnings.catch_warnings(record=True))
            self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            self.stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            warnings.simplefilter("always")
            self.closed = False

        def __call__(self):
            if phase == "invoke":
                raise failure
            return "value"

        def close(self):
            if not self.closed:
                self.stack.close()
                self.closed = True

    owner = Owner()

    def observe(value):
        owner.close()
        assert value == "value"
        if phase == "observe":
            raise failure
        return {"complete": True}

    rss_calls, clock_calls = [0], [0]

    def usage(_):
        rss_calls[0] += 1
        if (rss_calls[0] == 1 and phase == "setup_rss") or (
            rss_calls[0] == 2 and phase == "post_rss"
        ):
            raise failure
        return SimpleNamespace(ru_maxrss=10)

    def clock():
        clock_calls[0] += 1
        if (clock_calls[0] == 1 and phase == "first_clock") or (
            clock_calls[0] == 2 and phase == "second_clock"
        ):
            raise failure
        return clock_calls[0]

    monkeypatch.setattr(suite, "prepare", lambda _: (owner, observe))
    monkeypatch.setattr(resource, "getrusage", usage)
    monkeypatch.setattr(suite.time, "perf_counter_ns", clock)
    try:
        with pytest.raises(Failure) as error:
            suite.worker(JOB, 1, "time")
        assert error.value is failure and error.value.args == ("exact", phase)
        assert owner.closed
        assert_restored(before)
    finally:
        owner.close()
