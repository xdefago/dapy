# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Model representing trace data for visualization."""

from dataclasses import dataclass, field
from typing import Optional, Self

import networkx as nx
from dapy.core import Pid
from dapy.core.event import Message, Event
from dapy.sim import Trace


@dataclass(frozen=True)
class LamportClock:
    """Lamport logical clock for tracking event ordering."""
    _value: int = 0
    
    @classmethod
    def create(cls, initial_value: int = 0) -> Self:
        """Create a new Lamport clock.
        
        Args:
            initial_value: Initial clock value (defaults to 0).
            
        Returns:
            A new LamportClock instance.
        """
        return cls(_value=initial_value)
    
    def increment(self) -> Self:
        """Increment the clock.
        
        Returns:
            A new LamportClock with value + 1.
        """
        return type(self)(_value=self._value + 1)
    
    def merge(self, other: Self) -> Self:
        """Take maximum with another Lamport clock.
        
        Args:
            other: The Lamport clock to merge with.
            
        Returns:
            A new LamportClock with max value.
        """
        return type(self)(_value=max(self._value, other._value))
    
    def merge_and_increment(self, other: Self) -> Self:
        """Merge with another clock and increment.
        
        Args:
            other: The Lamport clock to merge with.
            
        Returns:
            A new LamportClock with max(self, other) + 1.
        """
        return type(self)(_value=max(self._value, other._value) + 1)
    
    def value(self) -> int:
        """Get the clock value.
        
        Returns:
            The current clock value.
        """
        return self._value
    
    def __eq__(self, other: object) -> bool:
        """Check if two Lamport clocks are equal.
        
        Args:
            other: Another Lamport clock or integer.
            
        Returns:
            True if values are equal.
        """
        if isinstance(other, LamportClock):
            return self._value == other._value
        if isinstance(other, int):
            return self._value == other
        return False
    
    def __lt__(self, other: Self) -> bool:
        """Check if this clock is less than another.
        
        Args:
            other: Another Lamport clock.
            
        Returns:
            True if self.value < other.value.
        """
        return self._value < other._value
    
    def __le__(self, other: Self) -> bool:
        """Check if this clock is less than or equal to another.
        
        Args:
            other: Another Lamport clock.
            
        Returns:
            True if self.value <= other.value.
        """
        return self._value <= other._value
    
    def __gt__(self, other: Self) -> bool:
        """Check if this clock is greater than another.
        
        Args:
            other: Another Lamport clock.
            
        Returns:
            True if self.value > other.value.
        """
        return self._value > other._value
    
    def __ge__(self, other: Self) -> bool:
        """Check if this clock is greater than or equal to another.
        
        Args:
            other: Another Lamport clock.
            
        Returns:
            True if self.value >= other.value.
        """
        return self._value >= other._value
    
    def __int__(self) -> int:
        """Convert to integer.
        
        Returns:
            The clock value as an integer.
        """
        return self._value
    
    def __repr__(self) -> str:
        """String representation.
        
        Returns:
            String showing the clock value.
        """
        return f"LamportClock({self._value})"


@dataclass(frozen=True)
class VectorClock:
    """Fidge-Mattern vector clock for tracking causality."""
    _clock: dict[Pid, int] = field(default_factory=dict)
    
    @classmethod
    def create(cls, processes: set[Pid], initial_values: Optional[dict[Pid, int]] = None) -> Self:
        """Create a new vector clock.
        
        Args:
            processes: Set of all process IDs in the system.
            initial_values: Optional initial clock values (defaults to all zeros).
            
        Returns:
            A new VectorClock instance.
        """
        if initial_values:
            clock = initial_values.copy()
        else:
            clock = {pid: 0 for pid in processes}
        return cls(_clock=clock)
    
    def increment(self, pid: Pid) -> Self:
        """Increment the clock component for a specific process.
        
        Args:
            pid: Process ID whose component to increment.
            
        Returns:
            A new VectorClock with the incremented value.
        """
        new_clock = self._clock.copy()
        new_clock[pid] += 1
        return type(self)(_clock=new_clock)
    
    def merge(self, other: Self) -> Self:
        """Take componentwise maximum with another vector clock.
        
        Args:
            other: The vector clock to merge with.
            
        Returns:
            A new VectorClock with merged values.
        """
        new_clock = self._clock.copy()
        for pid in new_clock:
            new_clock[pid] = max(new_clock[pid], other._clock.get(pid, 0))
        return type(self)(_clock=new_clock)
    
    def copy(self) -> Self:
        """Create a deep copy of this vector clock.
        
        Returns:
            A new VectorClock with the same values.
        """
        return type(self)(_clock=self._clock.copy())
    
    def to_lamport(self) -> int:
        """Convert to Lamport-like scalar clock.
        
        Returns:
            Sum of all components.
        """
        return sum(self._clock.values())
    
    def to_dict(self) -> dict[Pid, int]:
        """Get the underlying dictionary representation.
        
        Returns:
            Dictionary mapping process IDs to clock values.
        """
        return self._clock.copy()
    
    def __eq__(self, other: object) -> bool:
        """Check if two vector clocks are equal.
        
        Args:
            other: Another vector clock.
            
        Returns:
            True if all components are equal.
        """
        if not isinstance(other, VectorClock):
            return False
        return self._clock == other._clock
    
    def __lt__(self, other: Self) -> bool:
        """Check if this vector clock is less than another (causal precedence).
        
        Args:
            other: Another vector clock.
            
        Returns:
            True if self <= other componentwise and self != other.
        """
        all_pids = set(self._clock.keys()) | set(other._clock.keys())
        le = all(self._clock.get(pid, 0) <= other._clock.get(pid, 0) for pid in all_pids)
        return le and self != other
    
    def __le__(self, other: Self) -> bool:
        """Check if this vector clock is less than or equal to another.
        
        Args:
            other: Another vector clock.
            
        Returns:
            True if self <= other componentwise.
        """
        all_pids = set(self._clock.keys()) | set(other._clock.keys())
        return all(self._clock.get(pid, 0) <= other._clock.get(pid, 0) for pid in all_pids)
    
    def __gt__(self, other: Self) -> bool:
        """Check if this vector clock is greater than another.
        
        Args:
            other: Another vector clock.
            
        Returns:
            True if other < self.
        """
        return other < self
    
    def __ge__(self, other: Self) -> bool:
        """Check if this vector clock is greater than or equal to another.
        
        Args:
            other: Another vector clock.
            
        Returns:
            True if other <= self.
        """
        return other <= self
    
    def is_concurrent_with(self, other: Self) -> bool:
        """Check if two vector clocks are concurrent (incomparable).
        
        Args:
            other: Another vector clock.
            
        Returns:
            True if neither self < other nor other < self.
        """
        return not (self <= other) and not (other <= self)
    
    def __repr__(self) -> str:
        """String representation of the vector clock.
        
        Returns:
            String showing clock values.
        """
        return f"VectorClock({self._clock})"


@dataclass
class EventNode:
    """Represents an event in the trace."""
    pid: Pid
    event_type: str
    time: float  # Physical time (start)
    end_time: float  # Physical time (end/arrival)
    logical_time: LamportClock  # Lamport clock
    vector_clock: VectorClock  # Fidge-Mattern vector clock
    data: object
    index: int  # Position in trace
    is_send: bool = False  # True if this is a send event
    is_receive: bool = False  # True if this is a receive event
    sender: Optional[Pid] = None  # Sender if message
    receiver: Optional[Pid] = None  # Receiver if message


@dataclass
class MessageEdge:
    """Represents a message transmission."""
    sender: Pid
    receiver: Pid
    send_time: float  # Physical time when sent
    receive_time: float  # Physical time when received
    send_logical_time: LamportClock  # Logical time at sender
    receive_logical_time: LamportClock  # Logical time at receiver
    message_type: str
    message_data: object


class TraceModel:
    """Data model for trace visualization."""
    
    def __init__(self, trace: Trace) -> None:
        """Initialize trace model.
        
        Args:
            trace: The trace object to visualize.
        """
        self.trace = trace
        
        # Metadata from trace
        self.algorithm_name = trace.algorithm_name
        self.algorithm_description = trace.algorithm_description if hasattr(trace, 'algorithm_description') else ""
        self.synchrony_model_name = trace.synchrony_model_name if hasattr(trace, 'synchrony_model_name') else "Unknown"
        self.synchrony_model_params = trace.synchrony_model_params if hasattr(trace, 'synchrony_model_params') else {}
        self.trace_format_version = trace.trace_format_version if hasattr(trace, 'trace_format_version') else "1.0"
        
        # Extract processes
        self.processes: set[Pid] = set()
        
        # Extract events and messages
        self.events: list[EventNode] = []
        self.messages: list[MessageEdge] = []
        
        # Build network topology
        self.topology_graph = nx.Graph()
        
        # Vector clocks per process (Fidge-Mattern)
        self._vector_clocks: dict[Pid, VectorClock] = {}
        
        self._process_trace()
    
    def _process_trace(self) -> None:
        """Process the trace to extract events, messages, and topology."""
        # Extract processes and topology from system
        for pid in self.trace.system.topology.processes():
            self.processes.add(pid)
            self.topology_graph.add_node(pid)
        
        # Build topology edges from neighbors
        for pid in self.processes:
            for neighbor in self.trace.system.topology.neighbors_of(pid):
                if not self.topology_graph.has_edge(pid, neighbor):
                    self.topology_graph.add_edge(pid, neighbor)
        
        # Initialize vector clocks and Lamport clocks for each process
        self._lamport_clocks: dict[Pid, LamportClock] = {}
        for pid in self.processes:
            self._vector_clocks[pid] = VectorClock.create(self.processes)
            self._lamport_clocks[pid] = LamportClock.create()
        
        # Build a list of all atomic events (sends and receives) in trace order
        # Format: (trace_order, event_type, process_id, event_data)
        # event_type: 'send', 'receive', or 'local'
        # Process in TRACE ORDER, not real-time order, to maintain causality
        atomic_events: list[tuple[int, str, Pid, tuple]] = []
        
        for idx, timed_event in enumerate(self.trace.events_list):
            start = timed_event.start.total_seconds()  # Real time when sent
            end = timed_event.end.total_seconds()      # Real time when received
            event = timed_event.event
            
            assert isinstance(event, Event), "Only Event instances are supported in trace."
            is_message = isinstance(event, Message)
            
            if is_message:
                sender = event.sender
                receiver = event.target
                # Add send event at sender (processes first in trace order)
                atomic_events.append((idx * 2, 'send', sender, (event, idx, start, end, receiver)))
                # Add receive event at receiver (processes second in trace order)
                atomic_events.append((idx * 2 + 1, 'receive', receiver, (event, idx, start, end, sender)))
            else:
                # Signal/local event at target
                target = event.target
                atomic_events.append((idx * 2, 'local', target, (event, idx, start, end)))
        
        # Events are already in trace order; no need to sort by real time
        
        # Track send events for message edge construction
        # Key: (sender, receiver, trace_idx) -> (send_logical_time, send_vector_clock)
        send_info: dict[tuple[Pid, Pid, int], tuple[LamportClock, VectorClock]] = {}
        
        # Track unique event node index (separate from trace index)
        event_node_index = 0
        
        # Process atomic events in trace order (causally consistent)
        for trace_order, event_type, process_id, event_data in atomic_events:
            if event_type == 'send':
                event, orig_idx, start, end, receiver = event_data
                # Send: increment both Lamport and vector clocks
                self._lamport_clocks[process_id] = self._lamport_clocks[process_id].increment()
                self._vector_clocks[process_id] = self._vector_clocks[process_id].increment(process_id)
                
                send_lamport = self._lamport_clocks[process_id]
                send_vc = self._vector_clocks[process_id].copy()
                
                # Record for later when processing the receive (use trace index, not time)
                send_info[(process_id, receiver, orig_idx)] = (send_lamport, send_vc)
                
                # Create event node for the send
                event_node = EventNode(
                    pid=process_id,
                    event_type=type(event).__name__,
                    time=start,
                    end_time=start,  # Send is instantaneous at sender
                    logical_time=send_lamport,
                    vector_clock=send_vc.copy(),
                    data=event,
                    index=event_node_index,
                    is_send=True,
                    is_receive=False,
                    sender=process_id,
                    receiver=receiver
                )
                self.events.append(event_node)
                event_node_index += 1
                
            elif event_type == 'receive':
                event, orig_idx, start, end, sender = event_data
                # Receive: apply both Lamport and Fidge-Mattern rules
                send_key = (sender, process_id, orig_idx)
                sender_lamport, sender_vc = send_info[send_key]
                
                # Lamport clock: take max with sender's clock and increment
                self._lamport_clocks[process_id] = self._lamport_clocks[process_id].merge_and_increment(sender_lamport)
                
                # Vector clock: merge with sender's clock and increment own component
                self._vector_clocks[process_id] = self._vector_clocks[process_id].merge(sender_vc).increment(process_id)
                
                receive_lamport = self._lamport_clocks[process_id]
                receive_vc = self._vector_clocks[process_id].copy()
                
                # Create event node for the receive
                event_node = EventNode(
                    pid=process_id,
                    event_type=type(event).__name__,
                    time=start,
                    end_time=end,
                    logical_time=receive_lamport,
                    vector_clock=receive_vc.copy(),
                    data=event,
                    index=event_node_index,
                    is_send=False,
                    is_receive=True,
                    sender=sender,
                    receiver=process_id
                )
                self.events.append(event_node)
                event_node_index += 1
                
                # Build message edge
                msg_edge = MessageEdge(
                    sender=sender,
                    receiver=process_id,
                    send_time=start,
                    receive_time=end,
                    send_logical_time=sender_lamport,
                    receive_logical_time=receive_lamport,
                    message_type=type(event).__name__,
                    message_data=event
                )
                self.messages.append(msg_edge)
                
            else:  # 'local'
                event, orig_idx, start, end = event_data
                # Local event: increment both Lamport and vector clocks
                self._lamport_clocks[process_id] = self._lamport_clocks[process_id].increment()
                self._vector_clocks[process_id] = self._vector_clocks[process_id].increment(process_id)
                
                local_lamport = self._lamport_clocks[process_id]
                local_vc = self._vector_clocks[process_id].copy()
                
                # Create event node
                event_node = EventNode(
                    pid=process_id,
                    event_type=type(event).__name__,
                    time=start,
                    end_time=end,
                    logical_time=local_lamport,
                    vector_clock=local_vc.copy(),
                    data=event,
                    index=event_node_index,
                    is_send=False,
                    is_receive=False,
                    sender=None,
                    receiver=None
                )
                self.events.append(event_node)
                event_node_index += 1
    
    def _get_clock_at_time(self, timeline: list[tuple[float, int]], time: float) -> int:
        """Get the clock value at a specific time from a timeline.
        
        Args:
            timeline: List of (time, clock) tuples in chronological order.
            time: The time to query.
            
        Returns:
            The clock value at or before the given time.
        """
        result = 0
        for t, clock in timeline:
            if t <= time:
                result = clock
            else:
                break
        return result
    
    def get_processes_sorted(self) -> list[Pid]:
        """Get list of processes sorted by ID.
        
        Returns:
            Sorted list of process IDs.
        """
        return sorted(self.processes, key=lambda p: p.id)
    
    def get_events_for_process(self, pid: Pid) -> list[EventNode]:
        """Get all events for a specific process.
        
        Args:
            pid: Process identifier.
            
        Returns:
            List of events for the process, sorted by time.
        """
        process_events = [e for e in self.events if e.pid == pid]
        return sorted(process_events, key=lambda e: e.time)
    
    def get_time_range(self) -> tuple[float, float]:
        """Get the physical time range of the trace.
        
        Returns:
            Tuple of (min_time, max_time).
        """
        if not self.events:
            return (0.0, 1.0)
        
        # Use both start and end times
        min_time = min(e.time for e in self.events)
        max_time = max(e.end_time for e in self.events)
        
        # Add margin
        duration = max_time - min_time
        margin = duration * 0.05 if duration > 0 else 0.1
        return (min_time, max_time + margin)
    
    def get_logical_time_range(self) -> tuple[int, int]:
        """Get the logical time range of the trace.
        
        Returns:
            Tuple of (min_logical_time, max_logical_time).
        """
        if not self.events:
            return (1, 2)
        
        logical_times = [e.logical_time.value() for e in self.events]
        min_lt = min(logical_times)
        max_lt = max(logical_times)
        
        # Ensure we start from at least 1
        if min_lt < 1:
            min_lt = 1
        
        return (min_lt, max_lt + 1)
    
    def get_event_at_position(self, pid: Pid, time: float, tolerance: float = 0.1) -> Optional[EventNode]:
        """Find an event near a given position.
        
        Args:
            pid: Process identifier.
            time: Time coordinate.
            tolerance: How close the time must be.
            
        Returns:
            The event if found, None otherwise.
        """
        for event in self.events:
            if event.pid == pid:
                if abs(event.time - time) <= tolerance or abs(event.end_time - time) <= tolerance:
                    return event
        return None
    
    def get_message_at_position(self, time: float, tolerance: float = 0.1) -> Optional[MessageEdge]:
        """Find a message near a given position.
        
        Args:
            time: Time coordinate.
            tolerance: How close the time must be.
            
        Returns:
            The message if found, None otherwise.
        """
        for msg in self.messages:
            if msg.send_time - tolerance <= time <= msg.receive_time + tolerance:
                return msg
        return None
    
    def causally_precedes(self, event1: EventNode, event2: EventNode) -> bool:
        """Check if event1 causally precedes event2.
        
        Args:
            event1: First event.
            event2: Second event.
            
        Returns:
            True if event1 -> event2 (event1 causally precedes event2).
        """
        return event1.vector_clock < event2.vector_clock
    
    def are_concurrent(self, event1: EventNode, event2: EventNode) -> bool:
        """Check if two events are concurrent (not causally related).
        
        Args:
            event1: First event.
            event2: Second event.
            
        Returns:
            True if events are concurrent.
        """
        return event1.vector_clock.is_concurrent_with(event2.vector_clock)
    
    def get_causal_past(self, event: EventNode) -> list[EventNode]:
        """Get all events in the causal past of the given event.
        
        Args:
            event: The event to find causal past for.
            
        Returns:
            List of events that causally precede the given event.
        """
        return [e for e in self.events if e != event and self.causally_precedes(e, event)]
    
    def get_causal_future(self, event: EventNode) -> list[EventNode]:
        """Get all events in the causal future of the given event.
        
        Args:
            event: The event to find causal future for.
            
        Returns:
            List of events that the given event causally precedes.
        """
        return [e for e in self.events if e != event and self.causally_precedes(event, e)]
