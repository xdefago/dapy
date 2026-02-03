# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from abc import ABC
from dataclasses import dataclass, field
from datetime import timedelta
from itertools import count

from ..core import Event
from .configuration import Configuration

# Global counter for maintaining insertion order as a tie-breaker in heaps
_timed_event_counter = count()


@dataclass(frozen=True, order=True)
class Timed(ABC):
    """Abstract base class for objects with an associated timestamp.
    
    Attributes:
        time: The timestamp associated with this object.
    """
    time: timedelta


@dataclass(frozen=True, order=True)
class TimedEvent(Timed):
    """Represents an event associated with a specific time.
    
    When events have the same time, they are ordered by insertion order using
    an internal counter, avoiding the need to compare Event objects directly.
    
    Attributes:
        time: The time when the event occurs.
        event: The event object.
        _counter: Internal counter for maintaining insertion order as tie-breaker.
    """
    event: Event
    _counter: int = field(default_factory=lambda: next(_timed_event_counter), compare=True)


@dataclass(frozen=True, order=True)
class TimedConfiguration(Timed):
    """Represents a system configuration at a specific time.
    
    Attributes:
        time: The time when this configuration was active.
        configuration: The configuration object.
    """
    configuration: Configuration

