# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Tests for VectorClock implementation."""

from dapy.core import Pid
from dapyview.trace_model import VectorClock


class TestVectorClockBasics:
    """Test basic VectorClock operations."""
    
    def test_create_empty(self) -> None:
        """Test creating a vector clock with all zeros."""
        processes = {Pid(0), Pid(1), Pid(2)}
        vc = VectorClock.create(processes)
        
        assert vc.to_dict() == {Pid(0): 0, Pid(1): 0, Pid(2): 0}
        assert vc.to_lamport() == 0
    
    def test_create_with_initial_values(self) -> None:
        """Test creating a vector clock with initial values."""
        processes = {Pid(0), Pid(1), Pid(2)}
        initial = {Pid(0): 1, Pid(1): 2, Pid(2): 3}
        vc = VectorClock.create(processes, initial)
        
        assert vc.to_dict() == initial
        assert vc.to_lamport() == 6
    
    def test_increment(self) -> None:
        """Test incrementing a component."""
        processes = {Pid(0), Pid(1), Pid(2)}
        vc = VectorClock.create(processes)
        
        vc1 = vc.increment(Pid(0))
        assert vc1.to_dict() == {Pid(0): 1, Pid(1): 0, Pid(2): 0}
        
        vc2 = vc1.increment(Pid(0))
        assert vc2.to_dict() == {Pid(0): 2, Pid(1): 0, Pid(2): 0}
        
        vc3 = vc2.increment(Pid(1))
        assert vc3.to_dict() == {Pid(0): 2, Pid(1): 1, Pid(2): 0}
    
    def test_immutability(self) -> None:
        """Test that vector clocks are immutable."""
        processes = {Pid(0), Pid(1)}
        vc = VectorClock.create(processes)
        vc_incremented = vc.increment(Pid(0))
        
        # Original should be unchanged
        assert vc.to_dict() == {Pid(0): 0, Pid(1): 0}
        # New clock should have the increment
        assert vc_incremented.to_dict() == {Pid(0): 1, Pid(1): 0}
    
    def test_copy(self) -> None:
        """Test copying a vector clock."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 5, Pid(1): 3})
        vc2 = vc1.copy()
        
        assert vc1.to_dict() == vc2.to_dict()
        assert vc1 == vc2
        # Should be a different object
        assert vc1 is not vc2


class TestVectorClockMerge:
    """Test vector clock merge operation."""
    
    def test_merge_basic(self) -> None:
        """Test basic merge operation."""
        processes = {Pid(0), Pid(1), Pid(2)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2, Pid(2): 0})
        vc2 = VectorClock.create(processes, {Pid(0): 0, Pid(1): 1, Pid(2): 3})
        
        merged = vc1.merge(vc2)
        assert merged.to_dict() == {Pid(0): 1, Pid(1): 2, Pid(2): 3}
    
    def test_merge_identical(self) -> None:
        """Test merging identical clocks."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 5, Pid(1): 3})
        vc2 = VectorClock.create(processes, {Pid(0): 5, Pid(1): 3})
        
        merged = vc1.merge(vc2)
        assert merged.to_dict() == {Pid(0): 5, Pid(1): 3}
    
    def test_merge_immutability(self) -> None:
        """Test that merge doesn't modify original clocks."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 0})
        vc2 = VectorClock.create(processes, {Pid(0): 0, Pid(1): 2})
        
        merged = vc1.merge(vc2)
        
        # Originals should be unchanged
        assert vc1.to_dict() == {Pid(0): 1, Pid(1): 0}
        assert vc2.to_dict() == {Pid(0): 0, Pid(1): 2}
        # Merged should have max of both
        assert merged.to_dict() == {Pid(0): 1, Pid(1): 2}


class TestVectorClockComparisons:
    """Test vector clock comparison operators."""
    
    def test_equality(self) -> None:
        """Test equality comparison."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        vc2 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        vc3 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 3})
        
        assert vc1 == vc2
        assert not (vc1 == vc3)
    
    def test_less_than(self) -> None:
        """Test less than (causal precedence)."""
        processes = {Pid(0), Pid(1), Pid(2)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2, Pid(2): 0})
        vc2 = VectorClock.create(processes, {Pid(0): 2, Pid(1): 3, Pid(2): 1})
        vc3 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2, Pid(2): 0})
        
        assert vc1 < vc2  # vc1 causally precedes vc2
        assert not (vc2 < vc1)  # vc2 does not precede vc1
        assert not (vc1 < vc3)  # Equal clocks don't satisfy <
    
    def test_less_than_or_equal(self) -> None:
        """Test less than or equal."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        vc2 = VectorClock.create(processes, {Pid(0): 2, Pid(1): 3})
        vc3 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        
        assert vc1 <= vc2
        assert vc1 <= vc3  # Equal clocks satisfy <=
        assert not (vc2 <= vc1)
    
    def test_greater_than(self) -> None:
        """Test greater than."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        vc2 = VectorClock.create(processes, {Pid(0): 2, Pid(1): 3})
        
        assert vc2 > vc1
        assert not (vc1 > vc2)
    
    def test_greater_than_or_equal(self) -> None:
        """Test greater than or equal."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        vc2 = VectorClock.create(processes, {Pid(0): 2, Pid(1): 3})
        vc3 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        
        assert vc2 >= vc1
        assert vc1 >= vc3  # Equal clocks satisfy >=
        assert not (vc1 >= vc2)


class TestVectorClockConcurrency:
    """Test concurrency detection."""
    
    def test_concurrent_events(self) -> None:
        """Test detection of concurrent events."""
        processes = {Pid(0), Pid(1), Pid(2)}
        # Event at P0: [1, 0, 0]
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 0, Pid(2): 0})
        # Event at P1: [0, 1, 0]
        vc2 = VectorClock.create(processes, {Pid(0): 0, Pid(1): 1, Pid(2): 0})
        
        assert vc1.is_concurrent_with(vc2)
        assert vc2.is_concurrent_with(vc1)
    
    def test_not_concurrent_causal(self) -> None:
        """Test that causally related events are not concurrent."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 0})
        vc2 = VectorClock.create(processes, {Pid(0): 2, Pid(1): 1})
        
        assert not vc1.is_concurrent_with(vc2)
        assert not vc2.is_concurrent_with(vc1)
    
    def test_not_concurrent_equal(self) -> None:
        """Test that equal clocks are not concurrent."""
        processes = {Pid(0), Pid(1)}
        vc1 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        vc2 = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        
        assert not vc1.is_concurrent_with(vc2)


class TestVectorClockScenarios:
    """Test realistic distributed system scenarios."""
    
    def test_message_passing_scenario(self) -> None:
        """Test Fidge-Mattern algorithm for message passing."""
        processes = {Pid(0), Pid(1)}
        
        # Initial state
        vc_p0 = VectorClock.create(processes)
        vc_p1 = VectorClock.create(processes)
        
        # P0 sends message (increment own component)
        vc_p0 = vc_p0.increment(Pid(0))
        assert vc_p0.to_dict() == {Pid(0): 1, Pid(1): 0}
        
        # P1 receives message (merge + increment)
        vc_p1 = vc_p1.merge(vc_p0).increment(Pid(1))
        assert vc_p1.to_dict() == {Pid(0): 1, Pid(1): 1}
        
        # Verify causality: send happened before receive
        send_vc = VectorClock.create(processes, {Pid(0): 1, Pid(1): 0})
        receive_vc = VectorClock.create(processes, {Pid(0): 1, Pid(1): 1})
        assert send_vc < receive_vc
    
    def test_three_process_scenario(self) -> None:
        """Test three-process communication scenario."""
        processes = {Pid(0), Pid(1), Pid(2)}
        
        vc_p0 = VectorClock.create(processes)
        vc_p1 = VectorClock.create(processes)
        vc_p2 = VectorClock.create(processes)
        
        # P0 does local event
        vc_p0 = vc_p0.increment(Pid(0))
        assert vc_p0.to_dict() == {Pid(0): 1, Pid(1): 0, Pid(2): 0}
        
        # P1 does local event
        vc_p1 = vc_p1.increment(Pid(1))
        assert vc_p1.to_dict() == {Pid(0): 0, Pid(1): 1, Pid(2): 0}
        
        # P0 and P1 events are concurrent
        assert vc_p0.is_concurrent_with(vc_p1)
        
        # P0 sends to P2
        vc_p0 = vc_p0.increment(Pid(0))
        send_vc = vc_p0.copy()
        
        # P2 receives from P0
        vc_p2 = vc_p2.merge(send_vc).increment(Pid(2))
        assert vc_p2.to_dict() == {Pid(0): 2, Pid(1): 0, Pid(2): 1}
        
        # P1's first event is concurrent with P2's receive
        assert vc_p1.is_concurrent_with(vc_p2)
        
        # P0's send causally precedes P2's receive
        assert send_vc < vc_p2
    
    def test_lamport_conversion(self) -> None:
        """Test conversion to Lamport-like scalar clock."""
        processes = {Pid(0), Pid(1), Pid(2)}
        vc = VectorClock.create(processes, {Pid(0): 3, Pid(1): 5, Pid(2): 2})
        
        assert vc.to_lamport() == 10  # Sum of all components
    
    def test_repr(self) -> None:
        """Test string representation."""
        processes = {Pid(0), Pid(1)}
        vc = VectorClock.create(processes, {Pid(0): 1, Pid(1): 2})
        
        repr_str = repr(vc)
        assert "VectorClock" in repr_str
        assert "Pid(0)" in repr_str or "0" in repr_str
        assert "1" in repr_str
        assert "2" in repr_str
