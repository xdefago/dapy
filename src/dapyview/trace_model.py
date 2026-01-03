# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Model representing trace data for visualization."""

from dataclasses import dataclass, field
from typing import Optional

import networkx as nx
from dapy.core import Pid
from dapy.core.event import Message, Event
from dapy.sim import Trace


@dataclass
class EventNode:
    """Represents an event in the trace."""
    pid: Pid
    event_type: str
    time: float  # Physical time (start)
    end_time: float  # Physical time (end/arrival)
    logical_time: int  # Lamport clock
    data: object
    index: int  # Position in trace
    is_message: bool = False  # True if this is a message receive event
    sender: Optional[Pid] = None  # Sender if message


@dataclass
class MessageEdge:
    """Represents a message transmission."""
    sender: Pid
    receiver: Pid
    send_time: float  # Physical time when sent
    receive_time: float  # Physical time when received
    send_logical_time: int  # Logical time at sender
    receive_logical_time: int  # Logical time at receiver
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
        
        # Extract processes
        self.processes: set[Pid] = set()
        
        # Extract events and messages
        self.events: list[EventNode] = []
        self.messages: list[MessageEdge] = []
        
        # Build network topology
        self.topology_graph = nx.Graph()
        
        # Lamport clocks per process
        self._lamport_clocks: dict[Pid, int] = {}
        
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
        
        # Initialize Lamport clocks
        for pid in self.processes:
            self._lamport_clocks[pid] = 0
        
        # First pass: collect all events with their times
        raw_events: list[tuple[float, float, object, int]] = []
        for idx, timed_event in enumerate(self.trace.events_list):
            start = timed_event.start.total_seconds()
            end = timed_event.end.total_seconds()
            raw_events.append((start, end, timed_event.event, idx))
        
        # Sort by end time (event happens at end time for processing order)
        raw_events.sort(key=lambda x: (x[1], x[0]))
        
        # Build a map to track sender clocks at send time
        # For message events, send_time (start) is when sender sent it
        # We need to compute what the sender's clock was at that time
        
        # First pass: create event nodes without Lamport clocks
        temp_events: list[tuple[EventNode, float]] = []  # (event, send_time for messages)
        
        for idx, (start, end, event, orig_idx) in enumerate(raw_events):
            assert isinstance(event, Event), "Only Event instances are supported in trace."
            is_message = isinstance(event, Message)
            sender = event.sender if is_message else None
            target = event.target
            
            event_node = EventNode(
                pid=target,
                event_type=type(event).__name__,
                time=start,
                end_time=end,
                logical_time=0,  # Will be computed
                data=event,
                index=idx,
                is_message=is_message,
                sender=sender
            )
            temp_events.append((event_node, start if is_message else -1))
        
        # Second pass: compute Lamport clocks correctly
        # For Lamport's algorithm:
        # - Local event: LC = LC + 1
        # - Send event: LC = LC + 1, attach LC to message
        # - Receive event: LC = max(LC, msg_LC) + 1
        
        # Track what each process's clock is after processing events up to a certain time
        process_clock_timeline: dict[Pid, list[tuple[float, int]]] = {
            pid: [(0.0, 0)] for pid in self.processes
        }
        
        for event_node, send_time in temp_events:
            pid = event_node.pid
            
            if event_node.is_message and event_node.sender:
                # This is a receive event
                # Get sender's clock at send time
                sender = event_node.sender
                sender_clock_at_send = self._get_clock_at_time(
                    process_clock_timeline[sender], send_time
                )
                
                # Receiver's current clock
                receiver_current = self._lamport_clocks[pid]
                
                # Lamport's rule: LC = max(local, msg_LC) + 1
                new_clock = max(receiver_current, sender_clock_at_send) + 1
                self._lamport_clocks[pid] = new_clock
            else:
                # Local/internal event: LC = LC + 1
                self._lamport_clocks[pid] += 1
                new_clock = self._lamport_clocks[pid]
            
            event_node.logical_time = new_clock
            
            # Record this clock value in the timeline
            process_clock_timeline[pid].append((event_node.end_time, new_clock))
        
        # Store events
        self.events = [e for e, _ in temp_events]
        
        # Build message edges
        for event in self.events:
            if event.is_message and event.sender:
                # Get sender's clock at send time
                sender_clock = self._get_clock_at_time(
                    process_clock_timeline[event.sender], event.time
                )
                
                msg_edge = MessageEdge(
                    sender=event.sender,
                    receiver=event.pid,
                    send_time=event.time,
                    receive_time=event.end_time,
                    send_logical_time=sender_clock,
                    receive_logical_time=event.logical_time,
                    message_type=event.event_type,
                    message_data=event.data
                )
                self.messages.append(msg_edge)
    
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
        
        logical_times = [e.logical_time for e in self.events]
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
