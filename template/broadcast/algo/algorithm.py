"""
Flooding Broadcast Algorithm - Template

This is a template distributed algorithm that you can modify.
It implements a simple flooding broadcast where an initiator
broadcasts a value to all processes in the network.
"""

from dataclasses import dataclass, field
from typing import Sequence

from dapy.core import Algorithm, Event, Message, Pid, Signal, State

# ============================================================================
# State Definition
# ============================================================================

@dataclass(frozen=True)
class BroadcastState(State):
    """
    State of each process in the broadcast algorithm.
    
    All state classes must:
    - Inherit from State
    - Be frozen dataclasses (immutable)
    - Have a 'pid' field (inherited from State)
    """
    
    # Has this process participated in the broadcast?
    has_sent: bool = False
    
    # Value being broadcast
    value: int | None = None
    
    # Set of processes this node has received from
    received_from: set[Pid] = field(default_factory=set)


# ============================================================================
# Messages and Signals
# ============================================================================

@dataclass(frozen=True)
class BroadcastMsg(Message):
    """
    Message for broadcasting a value.
    
    All messages must:
    - Inherit from Message
    - Be frozen dataclasses
    - Have 'target' and 'sender' fields (inherited from Message)
    """
    
    value: int


@dataclass(frozen=True)
class Start(Signal):
    """
    Signal to initiate the broadcast.
    
    Signals are local events (no sender).
    """
    pass


@dataclass(frozen=True)
class BroadcastComplete(Signal):
    """
    Signal indicating this process has completed broadcasting.
    """
    value: int


# ============================================================================
# Algorithm Implementation
# ============================================================================

@dataclass(frozen=True)
class BroadcastAlgorithm(Algorithm):
    """
    Simple flooding broadcast algorithm.
    
    When a process receives a value (or is initiated with Start signal):
    1. If not yet participated, save the value
    2. Forward the value to all neighbors (except sender)
    3. Mark as participated
    
    This ensures the value reaches all processes in the network.
    """
    
    @property
    def name(self) -> str:
        """Algorithm name (appears in traces)."""
        return "Flooding Broadcast"
    
    def initial_state(self, pid: Pid) -> BroadcastState:
        """
        Create the initial state for a process.
        
        Args:
            pid: The process identifier
            
        Returns:
            Initial state for this process
        """
        return BroadcastState(pid=pid)
    
    def on_event(
        self, 
        old_state: BroadcastState, 
        event: Event
    ) -> tuple[BroadcastState, Sequence[Event]]:
        """
        Handle an event and produce new state + outgoing events.
        
        Args:
            old_state: Current state of the process
            event: Event to handle (message or signal)
            
        Returns:
            Tuple of (new_state, list_of_events_to_send)
        """
        
        match event:
            
            # ----------------------------------------------------------------
            # Start signal: Initiate broadcast with value 42
            # ----------------------------------------------------------------
            case Start(_):
                return self._initiate_broadcast(old_state, value=42)
            
            # ----------------------------------------------------------------
            # Broadcast message: Receive and forward
            # ----------------------------------------------------------------
            case BroadcastMsg(_, sender, value):
                # Already participated? Ignore
                if old_state.has_sent:
                    return old_state, []
                
                # Participate: save value and forward
                new_state = old_state.cloned_with(
                    has_sent=True,
                    value=value,
                    received_from=old_state.received_from | {sender}
                )
                
                # Forward to all neighbors except sender
                neighbors = self.system.topology.neighbors_of(old_state.pid)
                messages = [
                    BroadcastMsg(target=neighbor, sender=old_state.pid, value=value)
                    for neighbor in neighbors
                    if neighbor != sender
                ]
                
                # Signal completion
                complete_signal = BroadcastComplete(
                    target=old_state.pid,
                    value=value
                )
                
                return new_state, [*messages, complete_signal]
            
            # ----------------------------------------------------------------
            # Broadcast complete: Just log (optional)
            # ----------------------------------------------------------------
            case BroadcastComplete(_, value):
                print(f"Process {old_state.pid} completed broadcast with value {value}")
                return old_state, []
            
            # ----------------------------------------------------------------
            # Unknown event type
            # ----------------------------------------------------------------
            case _:
                raise NotImplementedError(
                    f"Event {type(event).__name__} not handled by {self.name}"
                )
    
    def _initiate_broadcast(
        self, 
        state: BroadcastState, 
        value: int
    ) -> tuple[BroadcastState, Sequence[Event]]:
        """
        Helper: Initiate broadcast from this process.
        
        Args:
            state: Current state
            value: Value to broadcast
            
        Returns:
            Tuple of (new_state, messages_to_send)
        """
        # Update state
        new_state = state.cloned_with(
            has_sent=True,
            value=value
        )
        
        # Send to all neighbors
        neighbors = self.system.topology.neighbors_of(state.pid)
        messages = [
            BroadcastMsg(target=neighbor, sender=state.pid, value=value)
            for neighbor in neighbors
        ]
        
        return new_state, messages


# ============================================================================
# You can add your own algorithm below this line
# ============================================================================

# TODO: Define your own state class
# TODO: Define your own message/signal types
# TODO: Implement your algorithm logic
