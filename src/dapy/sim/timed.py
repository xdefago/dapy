from abc import ABC
from dataclasses import dataclass
from datetime import timedelta

from ..core import Event
from .configuration import Configuration


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
    
    Attributes:
        time: The time when the event occurs.
        event: The event object.
    """
    event: Event


@dataclass(frozen=True, order=True)
class TimedConfiguration(Timed):
    """Represents a system configuration at a specific time.
    
    Attributes:
        time: The time when this configuration was active.
        configuration: The configuration object.
    """
    configuration: Configuration
