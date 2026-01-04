# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Shared pytest fixtures and configuration for dapy tests."""

from datetime import timedelta
from typing import Optional

import pytest

from dapy.algo.learn import LearnGraphAlgorithm, Start
from dapy.core import Pid, Ring, Synchronous, System
from dapy.sim import Settings, Simulator, Trace


@pytest.fixture
def simple_ring_system() -> System:
    """Create a simple Ring system with 3 processes for testing."""
    return System(
        topology=Ring.of_size(3),
        synchrony=Synchronous(fixed_delay=timedelta(seconds=1)),
    )


@pytest.fixture
def trace_from_learn_algorithm(simple_ring_system: System) -> Optional[Trace]:
    """Generate a trace from the LearnGraphAlgorithm on a ring."""
    settings = Settings(enable_trace=True)
    system = simple_ring_system
    algorithm = LearnGraphAlgorithm(system)
    sim = Simulator.from_system(system, algorithm, settings=settings)

    # Run the simulation
    sim.start()
    sim.schedule_event(timedelta(seconds=0), Start(target=Pid(1)))
    sim.run_to_completion()

    return sim.trace
