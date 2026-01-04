# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Tests for LamportClock implementation."""

from dapyview.trace_model import LamportClock


class TestLamportClockBasics:
    """Test basic LamportClock operations."""
    
    def test_create_default(self) -> None:
        """Test creating a Lamport clock with default value."""
        lc = LamportClock.create()
        assert lc.value() == 0
        assert int(lc) == 0
    
    def test_create_with_value(self) -> None:
        """Test creating a Lamport clock with initial value."""
        lc = LamportClock.create(5)
        assert lc.value() == 5
        assert int(lc) == 5
    
    def test_increment(self) -> None:
        """Test incrementing a Lamport clock."""
        lc = LamportClock.create()
        
        lc1 = lc.increment()
        assert lc1.value() == 1
        
        lc2 = lc1.increment()
        assert lc2.value() == 2
        
        lc3 = lc2.increment()
        assert lc3.value() == 3
    
    def test_immutability(self) -> None:
        """Test that Lamport clocks are immutable."""
        lc = LamportClock.create(10)
        lc_incremented = lc.increment()
        
        # Original should be unchanged
        assert lc.value() == 10
        # New clock should have the increment
        assert lc_incremented.value() == 11
    
    def test_merge(self) -> None:
        """Test merging two Lamport clocks."""
        lc1 = LamportClock.create(5)
        lc2 = LamportClock.create(3)
        
        merged = lc1.merge(lc2)
        assert merged.value() == 5  # max(5, 3)
        
        merged2 = lc2.merge(lc1)
        assert merged2.value() == 5  # max(3, 5)
    
    def test_merge_and_increment(self) -> None:
        """Test merge and increment in one operation."""
        lc1 = LamportClock.create(5)
        lc2 = LamportClock.create(3)
        
        result = lc1.merge_and_increment(lc2)
        assert result.value() == 6  # max(5, 3) + 1
        
        result2 = lc2.merge_and_increment(lc1)
        assert result2.value() == 6  # max(3, 5) + 1
    
    def test_merge_and_increment_immutability(self) -> None:
        """Test that merge_and_increment doesn't modify originals."""
        lc1 = LamportClock.create(5)
        lc2 = LamportClock.create(8)
        
        result = lc1.merge_and_increment(lc2)
        
        # Originals should be unchanged
        assert lc1.value() == 5
        assert lc2.value() == 8
        # Result should be max + 1
        assert result.value() == 9


class TestLamportClockComparisons:
    """Test Lamport clock comparison operators."""
    
    def test_equality(self) -> None:
        """Test equality comparison."""
        lc1 = LamportClock.create(5)
        lc2 = LamportClock.create(5)
        lc3 = LamportClock.create(6)
        
        assert lc1 == lc2
        assert not (lc1 == lc3)
    
    def test_equality_with_int(self) -> None:
        """Test equality comparison with integers."""
        lc = LamportClock.create(5)
        
        assert lc == 5
        assert not (lc == 6)
    
    def test_less_than(self) -> None:
        """Test less than comparison."""
        lc1 = LamportClock.create(3)
        lc2 = LamportClock.create(5)
        lc3 = LamportClock.create(3)
        
        assert lc1 < lc2
        assert not (lc2 < lc1)
        assert not (lc1 < lc3)  # Equal values
    
    def test_less_than_or_equal(self) -> None:
        """Test less than or equal comparison."""
        lc1 = LamportClock.create(3)
        lc2 = LamportClock.create(5)
        lc3 = LamportClock.create(3)
        
        assert lc1 <= lc2
        assert lc1 <= lc3  # Equal values
        assert not (lc2 <= lc1)
    
    def test_greater_than(self) -> None:
        """Test greater than comparison."""
        lc1 = LamportClock.create(5)
        lc2 = LamportClock.create(3)
        
        assert lc1 > lc2
        assert not (lc2 > lc1)
    
    def test_greater_than_or_equal(self) -> None:
        """Test greater than or equal comparison."""
        lc1 = LamportClock.create(5)
        lc2 = LamportClock.create(3)
        lc3 = LamportClock.create(5)
        
        assert lc1 >= lc2
        assert lc1 >= lc3  # Equal values
        assert not (lc2 >= lc1)


class TestLamportClockScenarios:
    """Test realistic distributed system scenarios."""
    
    def test_local_events(self) -> None:
        """Test sequence of local events at one process."""
        lc = LamportClock.create()
        
        # Three local events
        lc = lc.increment()
        assert lc.value() == 1
        
        lc = lc.increment()
        assert lc.value() == 2
        
        lc = lc.increment()
        assert lc.value() == 3
    
    def test_message_passing(self) -> None:
        """Test Lamport clock update with message passing."""
        # Process P0
        lc_p0 = LamportClock.create()
        lc_p0 = lc_p0.increment()  # Local event, LC=1
        lc_p0 = lc_p0.increment()  # Send message, LC=2
        send_lc = lc_p0
        
        # Process P1
        lc_p1 = LamportClock.create()
        lc_p1 = lc_p1.increment()  # Local event, LC=1
        lc_p1 = lc_p1.merge_and_increment(send_lc)  # Receive message
        
        # P1's clock should be max(1, 2) + 1 = 3
        assert lc_p1.value() == 3
        assert send_lc.value() < lc_p1.value()  # Send happens before receive
    
    def test_concurrent_events(self) -> None:
        """Test that concurrent events can have different Lamport times."""
        # Process P0
        lc_p0 = LamportClock.create()
        lc_p0 = lc_p0.increment()  # LC=1
        
        # Process P1 (independent)
        lc_p1 = LamportClock.create()
        lc_p1 = lc_p1.increment()  # LC=1
        
        # Both have LC=1, but they are concurrent
        # Lamport clocks don't guarantee they differ for concurrent events
        assert lc_p0.value() == lc_p1.value()
    
    def test_multiple_messages(self) -> None:
        """Test multiple message exchanges."""
        # P0 sends message
        lc_p0 = LamportClock.create()
        lc_p0 = lc_p0.increment()  # LC=1
        send1_lc = lc_p0
        
        # P1 receives and sends
        lc_p1 = LamportClock.create()
        lc_p1 = lc_p1.merge_and_increment(send1_lc)  # LC=2
        send2_lc = lc_p1.increment()  # LC=3
        
        # P0 receives
        lc_p0 = lc_p0.merge_and_increment(send2_lc)  # LC=4
        
        assert lc_p0.value() == 4
        assert lc_p1.value() == 3
        assert send1_lc < send2_lc < lc_p0
    
    def test_repr(self) -> None:
        """Test string representation."""
        lc = LamportClock.create(42)
        repr_str = repr(lc)
        
        assert "LamportClock" in repr_str
        assert "42" in repr_str
    
    def test_int_conversion(self) -> None:
        """Test conversion to int."""
        lc = LamportClock.create(25)
        
        assert int(lc) == 25
        assert isinstance(int(lc), int)
