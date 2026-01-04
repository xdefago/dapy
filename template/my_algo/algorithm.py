# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""
Template algorithm implementation.

This file provides a starting point for implementing your own distributed algorithm.
Replace MyAlgorithm, MyState, MyMessage, and MySignal with your own types.
"""

from dataclasses import dataclass
from typing import Sequence

from dapy.core import Algorithm, Event, Message, Pid, Signal, State

#
# Define the State of a process in the algorithm.
#

@dataclass(frozen=True)
class MyState(State):
    """State of a process in the algorithm.
    
    State must be immutable (frozen=True). Use state.cloned_with() to create
    modified copies when transitioning to a new state.
    """
    # Inherited from State:
    #   pid: Pid  # Process identifier
    
    # Declare any other relevant fields for your algorithm's state:
    # counter: int = 0
    # has_decided: bool = False
    # received_values: frozenset[int] = field(default_factory=frozenset)
    # etc.
    pass  # Remove this and add your fields

#
# Define the messages and signals used in the algorithm.
#
# Messages are exchanged between processes (have sender and target).
# Signals are local events delivered to a single process (have target only).
#

@dataclass(frozen=True)
class MyMessage(Message):
    """A message exchanged between processes.
    
    Messages represent inter-process communication. They are sent from one
    process to another with delivery timing determined by the synchrony model.
    """
    # Inherited from Message:
    #   target: Pid   # Destination process
    #   sender: Pid   # Source process
    
    # Declare any other relevant fields for your message content:
    # value: int
    # sequence_number: int
    # etc.
    pass  # Remove this and add your fields

    
@dataclass(frozen=True)
class MySignal(Signal):
    """A signal (local event) delivered to a process.
    
    Signals represent internal events or external stimuli. They are delivered
    directly to a process without going through the network.
    """
    # Inherited from Signal:
    #   target: Pid   # Process that receives this signal
    
    # Declare any other relevant fields for your signal:
    # trigger_condition: str
    # etc.
    pass  # Remove this and add your fields

    
#
# Define the algorithm itself.
#

@dataclass(frozen=True)
class MyAlgorithm(Algorithm[MyState]):
    """Brief description of what this algorithm does.
    
    The description is automatically extracted from this docstring and included
    in trace files. This allows the dapyview tool to display algorithm information
    even without access to the original source code.
    
    Replace this with a description of your algorithm: what problem it solves,
    assumptions about the system (e.g., reliable channels, crash failures),
    and key properties it guarantees (e.g., agreement, termination).
    """
    # Inherited from Algorithm:
    #   system: System  # The distributed system (topology + synchrony model)
    
    # Optional: Override these class variables to customize metadata
    # algorithm_name: str = "My Algorithm"  # defaults to class name if not set
    # algorithm_description: str = ""  # defaults to docstring if not set
    
    #
    # MANDATORY: Define the initial state for each process
    #
    def initial_state(self, pid: Pid) -> MyState:
        """Create and return the initial state of a process.
        
        This method is called once for each process at the start of simulation
        to initialize its local state.
        
        Args:
            pid: The identifier of the process being initialized.
        
        Returns:
            The initial state for the process with the given pid.
        """
        return MyState(
            pid=pid,
            # Initialize any other relevant fields:
            # counter=0,
            # has_decided=False,
            # etc.
        )
    
    #
    # MANDATORY: Define how processes react to events
    #
    def on_event(self, old_state: MyState, event: Event) -> tuple[MyState, Sequence[Event]]:
        """Process an event and return the new state and any events to schedule.
        
        This is the core of your algorithm logic. It defines how a process transitions
        from one state to another in response to messages and signals, and what new
        events (messages to send, signals to emit) should be scheduled.
        
        Use pattern matching to handle different event types:
        
        match event:
            case MyMessage(value=v):
                # Handle MyMessage
                new_state = old_state.cloned_with(counter=old_state.counter + v)
                # Send messages to all neighbors
                neighbors = self.system.topology.neighbors_of(old_state.pid)
                messages = [MyMessage(target=neighbor, sender=old_state.pid, value=v)
                           for neighbor in neighbors]
                return new_state, messages
            
            case MySignal():
                # Handle MySignal
                new_state = old_state.cloned_with(has_decided=True)
                return new_state, []
            
            case _:
                # Unknown event type - no state change
                return old_state, []
        
        Args:
            old_state: The current state of the process.
            event: The event (Message or Signal) being delivered to the process.
        
        Returns:
            A tuple of (new_state, events_to_schedule):
            - new_state: The updated state after processing the event
            - events_to_schedule: A list of events to be scheduled (can be empty)
        """
        # TODO: Implement your algorithm logic here
        # Use pattern matching (match/case) to handle different event types
        # Create new state with: new_state = old_state.cloned_with(field=new_value)
        # Schedule events by returning them in the events list
        
        new_state = old_state  # Replace with actual state transition
        new_events: list[Event] = []  # Replace with events to schedule
        
        return new_state, new_events

    #
    # OPTIONAL: Define initialization logic
    #
    def on_start(self, init_state: MyState) -> tuple[MyState, Sequence[Event]]:
        """Optionally modify initial state and schedule initial events.
        
        This method is called for each process after initial_state() but before
        the simulation begins. It allows you to:
        1. Modify the initial state (though this is rarely needed)
        2. Schedule initial events (e.g., a Start signal for a designated initiator)
        
        If you don't need initial events, you can schedule them externally using
        sim.schedule_event() instead of implementing this method.
        
        Args:
            init_state: The initial state from initial_state().
        
        Returns:
            A tuple of (possibly_modified_state, initial_events):
            - The state (usually unchanged)
            - A list of initial events to schedule (can be empty)
        """
        # Example: Designate process 0 as initiator
        # if init_state.pid == Pid(0):
        #     return init_state, [MySignal(target=init_state.pid)]
        
        return init_state, []  # No initial events by default
