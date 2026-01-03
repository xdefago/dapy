"""Test suite for network topology implementations."""

import pytest
from typing import Optional

from dapy.core.topology import Pid, ProcessSet, Channel, NetworkTopology, CompleteGraph, Ring, Star, Arbitrary


# Helper functions for topology validation


def assert_all_processes_present(topology: NetworkTopology, processes: ProcessSet) -> None:
    """Assert that all processes are present in the topology."""
    for pid in processes.processes:
        assert pid in topology.processes()
        assert pid in topology


def assert_no_self_neighbors(topology: NetworkTopology) -> None:
    """Assert that no process is its own neighbor in the topology."""
    for pid in topology.processes().processes:
        assert pid not in topology.neighbors_of(pid).processes


def assert_valid_topology(topology: NetworkTopology, size: int, processes: Optional[ProcessSet] = None) -> None:
    """Assert that a topology is valid (basic properties)."""
    if processes is None:
        processes = ProcessSet(Pid(i + 1) for i in range(size))
    
    assert topology.processes() == processes
    assert len(topology) == size
    assert len(topology.processes()) == size
    
    # Get min and max from processes attribute
    pids = list(processes.processes)
    min_pid = min(pids)
    max_pid = max(pids)
    assert Pid(min_pid.id - 1) not in topology
    assert min_pid in topology
    assert max_pid in topology
    assert Pid(max_pid.id + 1) not in topology
    
    assert_all_processes_present(topology, processes)
    assert_no_self_neighbors(topology)


def assert_valid_ring(topology: NetworkTopology, size: int, processes: Optional[ProcessSet] = None) -> None:
    """Assert that a Ring topology has correct neighbor relationships."""
    if processes is None:
        processes = ProcessSet(Pid(i + 1) for i in range(size))
    
    indexed_processes = list(processes.processes)
    
    # Check the neighbors of each process
    for i, pid in enumerate(processes.processes):
        prev = indexed_processes[i - 1]
        next_pid = indexed_processes[(i + 1) % size]
        assert len(topology.neighbors_of(pid)) == 2
        assert topology.neighbors_of(pid) == ProcessSet({prev, next_pid})


def assert_valid_complete_graph(topology: CompleteGraph, size: int, processes: Optional[ProcessSet] = None) -> None:
    """Assert that a CompleteGraph topology has all pairwise connections."""
    if processes is None:
        processes = ProcessSet(Pid(i + 1) for i in range(size))
    
    # Check the neighbors of each process
    for pid in processes.processes:
        assert len(topology.neighbors_of(pid)) == size - 1
        assert topology.neighbors_of(pid) + {pid} == topology.processes()


def assert_valid_star(topology: Star, size: int, processes: Optional[ProcessSet] = None) -> None:
    """Assert that a Star topology has correct hub-and-spoke structure."""
    if processes is None:
        processes = ProcessSet(Pid(i + 1) for i in range(size))
    
    # Check the neighbors of each process
    for pid in processes.processes:
        if pid == topology.center():
            assert len(topology.neighbors_of(pid)) == size - 1
            assert topology.neighbors_of(pid) + {pid} == topology.processes()
        else:
            assert len(topology.neighbors_of(pid)) == 1
            assert topology.neighbors_of(pid) == ProcessSet(topology.center())


# Test classes


class TestRingTopology:
    """Test suite for Ring topology."""

    @pytest.mark.parametrize("size", [4])
    def test_ring_of_size(self, size: int) -> None:
        """Test Ring topology with sequential process IDs."""
        topology = Ring.of_size(size)
        assert_valid_topology(topology, size)
        assert_valid_ring(topology, size)

    def test_ring_from_process_set(self) -> None:
        """Test Ring topology with custom process IDs."""
        processes = ProcessSet({Pid(10), Pid(20), Pid(30)})
        topology = Ring.from_(list(processes.processes))
        assert_valid_topology(topology, 3, processes)
        assert_valid_ring(topology, 3, processes)


class TestCompleteGraphTopology:
    """Test suite for CompleteGraph topology."""

    @pytest.mark.parametrize("size", [2, 4, 9])
    def test_complete_graph_of_size(self, size: int) -> None:
        """Test CompleteGraph topology with sequential process IDs."""
        topology = CompleteGraph.of_size(size)
        assert_valid_topology(topology, size)
        assert_valid_complete_graph(topology, size)

    def test_complete_graph_from_list(self) -> None:
        """Test CompleteGraph topology created from a list of PIDs."""
        topology = CompleteGraph.from_([Pid(1), Pid(2), Pid(3)])
        assert_valid_topology(topology, 3)
        assert_valid_complete_graph(topology, 3)

    def test_complete_graph_from_process_set(self) -> None:
        """Test CompleteGraph topology created from a ProcessSet."""
        processes = ProcessSet({Pid(10), Pid(20), Pid(30)})
        topology = CompleteGraph.from_(list(processes.processes))
        assert_valid_topology(topology, 3, processes)
        assert_valid_complete_graph(topology, 3, processes)


class TestStarTopology:
    """Test suite for Star topology."""

    @pytest.mark.parametrize("size", [2, 4, 9])
    def test_star_of_size(self, size: int) -> None:
        """Test Star topology with sequential process IDs."""
        topology = Star.of_size(size)
        assert_valid_topology(topology, size)
        assert_valid_star(topology, size)

    def test_star_from_center_and_leaves(self) -> None:
        """Test Star topology created from explicit center and leaves."""
        process_list = [Pid(10), Pid(20), Pid(30), Pid(40)]
        processes = ProcessSet(process_list)
        topology = Star.from_(process_list[0], process_list[1:])
        assert_valid_topology(topology, 4, processes)
        assert_valid_star(topology, 4, processes)

    def test_star_center_cannot_be_leaf(self) -> None:
        """Test that Star topology raises error when center is in leaves."""
        process_list = [Pid(10), Pid(20), Pid(30), Pid(40)]
        with pytest.raises(ValueError):
            Star.from_(process_list[0], process_list)

    def test_star_requires_multiple_leaves(self) -> None:
        """Test that Star topology requires at least 2 leaves."""
        process_list = [Pid(10), Pid(20), Pid(30), Pid(40)]
        with pytest.raises(ValueError):
            Star.from_(process_list[0], process_list[1:1])


class TestArbitraryTopology:
    """Test suite for Arbitrary topology."""

    def test_arbitrary_unconnected_from_process_set(self) -> None:
        """Test Arbitrary topology with no connections."""
        processes = ProcessSet({Pid(1), Pid(2), Pid(3)})
        topology = Arbitrary.from_(list(processes.processes))
        assert_valid_topology(topology, 3, processes)
        for pid in processes.processes:
            assert topology.neighbors_of(pid) == ProcessSet()

    def test_arbitrary_directed_ring_from_tuples(self) -> None:
        """Test Arbitrary topology with directed ring from tuples."""
        processes = ProcessSet({Pid(1), Pid(2), Pid(3)})
        channels = [
            (Pid(1), Pid(2)),
            (Pid(2), Pid(3)),
            (Pid(3), Pid(1)),
        ]
        topology = Arbitrary.from_(channels)
        assert_valid_topology(topology, 3, processes)
        for pid in processes.processes:
            assert len(topology.neighbors_of(pid)) == 1
            assert topology.neighbors_of(pid) == ProcessSet({Pid((pid.id % 3) + 1)})

    def test_arbitrary_undirected_ring_from_tuples(self) -> None:
        """Test Arbitrary topology with undirected ring from tuples."""
        processes = ProcessSet({Pid(1), Pid(2), Pid(3)})
        channels = [
            (Pid(1), Pid(2)),
            (Pid(2), Pid(3)),
            (Pid(3), Pid(1)),
        ]
        topology: NetworkTopology = Arbitrary.from_(channels, directed=False)
        assert_valid_topology(topology, 3, processes)
        assert_valid_ring(topology, 3, processes)

    def test_arbitrary_undirected_ring_from_channels(self) -> None:
        """Test Arbitrary topology with undirected ring from Channel objects."""
        processes = ProcessSet({Pid(1), Pid(2), Pid(3)})
        channels = [
            Channel(Pid(1), Pid(2)),
            Channel(Pid(2), Pid(3)),
            Channel(Pid(3), Pid(1)),
        ]
        topology: NetworkTopology = Arbitrary.from_(channels, directed=False)
        assert_valid_topology(topology, 3, processes)
        assert_valid_ring(topology, 3, processes)

    def test_arbitrary_undirected_ring_from_mixed_objects(self) -> None:
        """Test Arbitrary topology with mixed object types (Pid, tuples, Channels)."""
        processes = ProcessSet({Pid(1), Pid(2), Pid(3)})
        channels = [
            Pid(1),
            Pid(2),
            Channel(Pid(1), Pid(2)),
            (Pid(2), Pid(3)),
            Channel(Pid(3), Pid(1)),
        ]
        topology: NetworkTopology = Arbitrary.from_(channels, directed=False)
        assert_valid_topology(topology, 3, processes)
        assert_valid_ring(topology, 3, processes)
    