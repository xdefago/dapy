# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Tests for core classes without existing coverage."""

from __future__ import annotations

from dataclasses import dataclass

import random

import pytest

from dapy.core import (
    Algorithm,
    Asynchronous,
    Channel,
    ChannelSet,
    Event,
    Message,
    PartiallySynchronous,
    Pid,
    ProcessSet,
    Ring,
    Signal,
    State,
    StochasticExponential,
    Synchronous,
    System,
    simtime,
)


def test_pid_basics() -> None:
    pid = Pid(3)
    assert str(pid) == "p3"
    assert repr(pid) == "Pid(3)"
    assert Pid(pid) == pid
    with pytest.raises(ValueError):
        Pid(-1)


def test_process_set_operations() -> None:
    p1, p2 = Pid(1), Pid(2)
    ps = ProcessSet(p1)
    assert p1 in ps
    assert len(ps) == 1
    assert list(sorted(ps)) == [p1]

    ps2 = ps + p2
    assert len(ps2) == 2
    assert p2 in ps2

    ps3 = ps2 + ProcessSet({Pid(3)})
    assert len(ps3) == 3

    ps4 = ps3 + [Pid(4)]
    assert Pid(4) in ps4

    with pytest.raises(TypeError):
        _ = ps + 123  # type: ignore[operator]


def test_channel_equality_and_hash() -> None:
    p1, p2 = Pid(1), Pid(2)
    c1 = Channel(p1, p2)
    c2 = Channel(p1, p2)
    c3 = Channel(p2, p1)
    assert c1 == c2
    assert c1 != c3
    assert hash(c1) == hash(c2)

    u1 = Channel(p1, p2, directed=False)
    u2 = Channel(p2, p1, directed=False)
    assert u1 == u2
    assert hash(u1) == hash(u2)


def test_channel_set_addition() -> None:
    p1, p2, p3 = Pid(1), Pid(2), Pid(3)
    c1 = Channel(p1, p2)
    c2 = Channel(p2, p3)

    cs = ChannelSet(c1)
    assert c1 in cs
    cs2 = cs + c2
    assert c2 in cs2

    cs3 = cs2 + ChannelSet({Channel(p3, p1)})
    assert len(cs3) == 3

    cs4 = cs3 + [Channel(p1, p3)]
    assert len(cs4) == 4

    with pytest.raises(TypeError):
        _ = cs + 123  # type: ignore[operator]


@dataclass(frozen=True)
class MySignal(Signal):
    value: int


@dataclass(frozen=True)
class MyMessage(Message):
    value: int


def test_event_str_and_ordering() -> None:
    s1 = MySignal(target=Pid(1), value=7)
    s2 = MySignal(target=Pid(2), value=7)
    assert str(s1) == "MySignal(@p1; value=7)"
    assert s1 < s2
    assert s2 > s1

    m = MyMessage(target=Pid(1), sender=Pid(2), value=9)
    assert str(m) == "MyMessage(@p1; sender=p2, value=9)"


@dataclass(frozen=True)
class MyState(State):
    counter: int = 0


def test_state_cloned_with_and_str() -> None:
    state = MyState(pid=Pid(1), counter=5)
    updated = state.cloned_with(counter=6)
    assert updated.counter == 6
    assert updated.pid == state.pid
    assert state.as_str() == "p1: counter=5"
    assert str(state) == "p1: counter=5"
    assert state.as_str(keys=["counter"]) == "p1: counter=5"


@dataclass(frozen=True)
class MyAlgorithm(Algorithm[MyState]):
    """Short description line.

    Attributes:
        ignored: This should not appear in the description.
    """

    def initial_state(self, pid: Pid) -> MyState:
        return MyState(pid=pid)

    def on_event(self, old_state: MyState, event: Event) -> tuple[MyState, list[Event]]:
        return old_state, []


@dataclass(frozen=True)
class NamedAlgorithm(MyAlgorithm):
    algorithm_name: str | None = "CustomName"
    algorithm_description: str | None = "Custom description."


def test_algorithm_name_and_description() -> None:
    system = System(topology=Ring.of_size(3))
    algo = MyAlgorithm(system)
    assert algo.name == "MyAlgorithm"
    assert algo.description == "Short description line."

    named = NamedAlgorithm(system)
    assert named.name == "CustomName"
    assert named.description == "Custom description."

    state = MyState(pid=Pid(1))
    assert algo.on_start(state) == (state, [])


def test_synchrony_models_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    sent_at = simtime(seconds=1)

    sync = Synchronous(fixed_delay=simtime(milliseconds=2))
    assert sync.arrival_time_for(sent_at) == sent_at + simtime(milliseconds=2)

    async_model = Asynchronous(base_delay=simtime(seconds=2))
    monkeypatch.setattr(random, "expovariate", lambda _lambd=None, **_kwargs: 0.0)
    monkeypatch.setattr(random, "uniform", lambda _a, _b: 0.0)
    assert async_model.arrival_time_for(sent_at) == sent_at + async_model.min_delay

    stochastic = StochasticExponential(delta_t=simtime(milliseconds=10))
    monkeypatch.setattr(random, "expovariate", lambda _lambd=None, **_kwargs: 1.5)
    assert stochastic.arrival_time_for(sent_at) == sent_at + stochastic.min_delay + simtime(milliseconds=15)


def test_partially_synchronous_lucky_path(monkeypatch: pytest.MonkeyPatch) -> None:
    sent_at = simtime(seconds=1)
    model = PartiallySynchronous(gst=simtime(seconds=10), fixed_delay=simtime(milliseconds=3))
    monkeypatch.setattr(random, "choice", lambda _choices: "lucky")
    assert model.arrival_time_for(sent_at) == sent_at + simtime(milliseconds=3)


def test_synchrony_model_validation() -> None:
    with pytest.raises(ValueError):
        _ = Synchronous(min_delay=simtime(seconds=0))
    with pytest.raises(ValueError):
        _ = Asynchronous(min_delay=simtime(seconds=0))
    with pytest.raises(ValueError):
        _ = StochasticExponential(delta_t=simtime(seconds=0))


def test_system_processes_and_neighbors() -> None:
    system = System(topology=Ring.of_size(3), synchrony=Asynchronous())
    processes = list(system.processes())
    assert len(processes) == 3
    assert system.neighbors_of(Pid(1)) == ProcessSet({Pid(2), Pid(3)})