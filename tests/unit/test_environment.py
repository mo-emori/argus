import pytest

from argus.runtime.environment import Environment


def test_valid_environment_test() -> None:
    assert Environment("TEST") is Environment.TEST


def test_valid_environment_paper() -> None:
    assert Environment("PAPER") is Environment.PAPER


def test_valid_environment_live() -> None:
    assert Environment("LIVE") is Environment.LIVE


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(ValueError):
        Environment("DEV")
        