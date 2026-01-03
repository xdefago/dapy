# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Iterable, Self

from ..core import Event, Message, Pid, Signal, System
from .configuration import Configuration
from .timed import TimedConfiguration


@dataclass(frozen=True, order=True)
class LocalTimedEvent:
    """Represents a timed event with transmission interval during simulation.
    
    Records the start time when an event is sent and the end time when it arrives,
    useful for understanding message delays in the simulation.
    
    Attributes:
        start: The time when the event was sent.
        end: The time when the event arrived at its destination.
        event: The event object (Message or Signal).
    """
    start: timedelta
    end: timedelta
    event: Event
    
    def is_message(self) -> bool:
        """Check if this timed event represents a message transmission.
        
        Returns:
            True if the event is a Message, False otherwise.
        """
        return isinstance(self.event, Message)
    
    def is_signal(self) -> bool:
        """Check if this timed event represents a signal.
        
        Returns:
            True if the event is a Signal, False otherwise.
        """
        return isinstance(self.event, Signal)
    
    def sender(self) -> Pid:
        """Get the sender/initiator of this event.
        
        For messages, returns the sender. For signals, returns the target.
        
        Returns:
            The process identifier of the event's sender/initiator.
        """
        return self.event.sender if isinstance(self.event, Message) else self.event.target
    
    def receiver(self) -> Pid:
        """Get the receiver of this event.
        
        Returns:
            The process identifier of the event's target/receiver.
        """
        return self.event.target


@dataclass
class Trace:
    """Represents the execution trace of a distributed algorithm simulation.
    
    A trace records both the events (messages and signals) exchanged between
    processes and the system configurations at various time points during
    the simulation.
    
    Attributes:
        system: The distributed system being simulated.
        algorithm_name: The name of the algorithm being executed.
        history: List of system configurations at specific time points.
        events_list: List of timed events during the simulation.
    """
    system: System
    algorithm_name: str
    
    history: list[TimedConfiguration] = field(default_factory=list)
    events_list: list[LocalTimedEvent] = field(default_factory=list)

    def add_events(self, events: Iterable[tuple[timedelta, timedelta, Event]]) -> None:
        """Add timed events to the trace.
        
        Message events require two timestamps: one for the send time at the sender
        and one for the arrival time at the receiver.
        
        Args:
            events: An iterable of (start_time, end_time, event) tuples where
                    start_time is when the event begins and end_time is when it completes.
        """
        self.events_list.extend(LocalTimedEvent(start, end, event) for start, end, event in events)

    def add_history(self, history: Iterable[tuple[timedelta, Configuration]]) -> None:
        """Add system configurations at specific time points to the trace.
        
        Args:
            history: An iterable of (time, configuration) tuples representing
                     the system state at each time point.
        """
        self.history.extend(TimedConfiguration(time, configuration) for time, configuration in history)

    def dump_pickle(self) -> bytes:
        """Serialize the trace to a pickle byte string.
        
        Returns:
            The serialized trace as bytes.
        """
        import pickle
        return pickle.dumps(self)
    
    @classmethod
    def load_pickle(cls, data: bytes) -> Self:
        """Deserialize a trace from a pickle byte string.
        
        Args:
            data: The serialized trace as bytes.
        
        Returns:
            A Trace instance deserialized from the byte string.
        
        Raises:
            TypeError: If the deserialized object is not a Trace instance.
        """
        import pickle
        obj = pickle.loads(data)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected Trace, got {type(obj)}")
        return obj

    def dump_json(self) -> str:
        """Serialize the trace to a JSON string.
        
        Returns:
            The serialized trace as a JSON string.
        
        Raises:
            ImportError: If classifiedjson is not installed. Install with:
                        uv pip install dapy[json]
        """
        try:
            from classifiedjson import dumps, is_exact_match
        except ImportError:
            raise ImportError("classifiedjson is not installed. Please re-install dapy with the json feature.")
        
        def _timedelta_serialize(obj: timedelta) -> str:
            """
            Serialize a timedelta object to a string.
            """
            if not is_exact_match(obj, timedelta):
                return NotImplemented
            return repr(obj)
        
        return dumps(self, custom_hooks=[_timedelta_serialize])

    @classmethod
    def load_json(cls, data: str) -> Self:
        """Deserialize a trace from a JSON string.
        
        Args:
            data: The serialized trace as a JSON string.
        
        Returns:
            A Trace instance deserialized from the JSON string.
        
        Raises:
            ImportError: If classifiedjson is not installed. Install with:
                        uv pip install dapy[json]
        """
        try:
            from classifiedjson import Factory, loads
        except ImportError:
            raise ImportError("classifiedjson is not installed. Please re-install dapy with the json feature.")
        
        def _timedelta_deserialize(factory: Factory, obj: str) -> timedelta:
            """
            Deserialize a string to a timedelta object.
            """
            if not factory.is_exact_match(timedelta):
                return NotImplemented
            return _parse_timedelta(obj)
        
        return loads(data, custom_hooks=[_timedelta_deserialize])  # type: ignore



def _parse_timedelta(timedelta_str: str) -> timedelta:
    """
    Parse a string to create a timedelta object.
    """
    import re
    match = re.match(r"^datetime.timedelta\((?P<args>.*)\)$", timedelta_str)
    if not match:
        raise ValueError(f"Invalid timedelta string: {timedelta_str}")
    
    args = match.group("args").split(",")
    kwargs = {}
    if args == ["0"]:
        return timedelta(0)
    
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=")
            kwargs[key.strip()] = eval(value.strip())
        else:
            kwargs[arg.strip()] = None
    
    return timedelta(**kwargs)



