"""
Tests for the broadcast algorithm

Run with: uv run pytest
"""

from dapy.core import System, Ring, Asynchronous, Pid
from dapy.sim import Simulator, Settings
from src.my_algo.algorithm import BroadcastAlgorithm, Start, BroadcastState


def test_broadcast_reaches_all_processes():
    """Test that broadcast value reaches all processes in a ring."""
    # Setup
    system = System(topology=Ring.of_size(5), synchrony=Asynchronous())
    algorithm = BroadcastAlgorithm(system)
    settings = Settings(enable_trace=False)
    
    sim = Simulator.from_system(system, algorithm, settings=settings)
    sim.start()
    
    # Initiate broadcast from process 0
    from datetime import timedelta
    sim.schedule_event(timedelta(seconds=0), Start(target=Pid(0)))
    
    # Run simulation
    sim.run_to_completion()
    
    # Verify all processes received the value
    for pid in range(5):
        state = sim.configuration.state(Pid(pid))
        assert isinstance(state, BroadcastState)
        assert state.has_sent, f"Process {pid} should have participated"
        assert state.value == 42, f"Process {pid} should have value 42"


def test_initial_state():
    """Test that initial state is correctly set."""
    system = System(topology=Ring.of_size(3), synchrony=Asynchronous())
    algorithm = BroadcastAlgorithm(system)
    
    initial = algorithm.initial_state(Pid(0))
    
    assert initial.pid == Pid(0)
    assert not initial.has_sent
    assert initial.value is None
    assert len(initial.received_from) == 0


def test_algorithm_name():
    """Test that algorithm has correct name."""
    system = System(topology=Ring.of_size(3), synchrony=Asynchronous())
    algorithm = BroadcastAlgorithm(system)
    
    assert algorithm.name == "Flooding Broadcast"
