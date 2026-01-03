"""Test suite for trace generation and serialization."""

from datetime import timedelta
from typing import Optional

from dapy.sim import Trace


class TestTraceGeneration:
    """Test suite for Trace generation and validation."""

    def test_trace_properties(self, trace_from_learn_algorithm: Optional[Trace]) -> None:
        """Test that generated trace has expected properties."""
        trace = trace_from_learn_algorithm
        assert trace is not None
        assert trace.algorithm_name == "Learn the Topology"
        assert len(trace.history) == 16
        assert len(trace.events_list) == 16
        assert len(trace.history[0].configuration) == 3
        assert trace.history[0].time == timedelta(seconds=0)
        assert trace.history[-1].time == timedelta(seconds=3)


class TestTraceSerialization:
    """Test suite for Trace serialization and deserialization."""

    def test_trace_json_serialization(self, trace_from_learn_algorithm: Optional[Trace]) -> None:
        """Test JSON serialization and deserialization of Trace."""
        original_trace = trace_from_learn_algorithm
        assert original_trace is not None
        trace_json = original_trace.dump_json()
        assert trace_json is not None
        assert isinstance(trace_json, str)
        
        # Deserialize from JSON
        restored_trace = Trace.load_json(trace_json)
        assert restored_trace == original_trace

    def test_trace_pickle_serialization(self, trace_from_learn_algorithm: Optional[Trace]) -> None:
        """Test Pickle serialization and deserialization of Trace."""
        original_trace = trace_from_learn_algorithm
        assert original_trace is not None
        trace_bytes = original_trace.dump_pickle()
        assert trace_bytes is not None
        assert isinstance(trace_bytes, bytes)
        
        # Deserialize from pickle
        restored_trace = Trace.load_pickle(trace_bytes)
        assert restored_trace == original_trace

    def test_trace_roundtrip_consistency(self, trace_from_learn_algorithm: Optional[Trace]) -> None:
        """Test that JSON and Pickle serialization preserve trace equality."""
        original_trace = trace_from_learn_algorithm
        assert original_trace is not None
        json_trace = Trace.load_json(original_trace.dump_json())
        # Test Pickle roundtrip
        pickle_trace = Trace.load_pickle(original_trace.dump_pickle())
        
        # Both should be equal to original
        assert json_trace == original_trace
        assert pickle_trace == original_trace
        # And equal to each other
        assert json_trace == pickle_trace
