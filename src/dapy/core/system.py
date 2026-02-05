# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

import random

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Iterable, NewType

from .pid import Pid, ProcessSet
from .topology import NetworkTopology


# Type alias for simulation time
SimTime = NewType('SimTime', timedelta)


def simtime(hours: float = 0, minutes: float = 0, seconds: float = 0,
            milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0,
            weeks: float = 0, days: float = 0) -> SimTime:
    """Create a SimTime value from time components.
    
    Provides a convenient factory function to create simulation time values
    without exposing the underlying timedelta implementation.
    
    Args:
        weeks: Number of weeks. Defaults to 0.
        days: Number of days. Defaults to 0.
        hours: Number of hours. Defaults to 0.
        minutes: Number of minutes. Defaults to 0.
        seconds: Number of seconds. Defaults to 0.
        milliseconds: Number of milliseconds. Defaults to 0.
        microseconds: Number of microseconds. Defaults to 0.
        nanoseconds: Number of nanoseconds. Defaults to 0.
    Returns:
        A SimTime value representing the specified duration.
    
    Examples:
        >>> simtime(seconds=5)
        datetime.timedelta(seconds=5)
        >>> simtime(milliseconds=100)
        datetime.timedelta(milliseconds=100)
        >>> simtime(minutes=1, seconds=30)
        datetime.timedelta(seconds=90)
    """
    return SimTime(timedelta(days=days, seconds=seconds, microseconds=microseconds + nanoseconds / 1000,
                             milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks))


SIMTIME_EPSILON = simtime(nanoseconds=1) # Smallest distinguishable time unit


@dataclass(frozen=True)
class SynchronyModel(ABC):
    min_delay: SimTime = field(default=simtime(nanoseconds=1))
    def __post_init__(self) -> None:
        if self.min_delay < SIMTIME_EPSILON:
            raise ValueError("Minimum delay must be strictly positive.")
        
    @abstractmethod
    def arrival_time_for(self, sent_at: SimTime) -> SimTime:
        """Calculate the arrival time for a message based on the synchrony model.
        
        Args:
            sent_at: The time when the message is sent.
        
        Returns:
            The time when the message should arrive.
        """

    
@dataclass(frozen=True)
class Synchronous(SynchronyModel):
    """Represents a synchronous system with bounded communication delays.
    
    In a synchronous system, all communication is bounded by a fixed time interval.
    Messages are guaranteed to arrive within this fixed delay.
    
    Attributes:
        fixed_delay: The maximum delay for all message deliveries. Defaults to 1 millisecond.
    """
    fixed_delay: SimTime = field(default_factory=lambda: simtime(milliseconds=1))
    
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.fixed_delay < self.min_delay:
            raise ValueError("The fixed delay must be at least as great as the minimum delay.")
    
    def arrival_time_for(self, sent_at: SimTime) -> SimTime:
        return SimTime(sent_at + self.fixed_delay)


@dataclass(frozen=True)
class Asynchronous(SynchronyModel):
    """Represents an asynchronous system with unbounded communication delays.
    
    In an asynchronous system, there are no bounds on message delivery times.
    Messages may be delayed arbitrarily but are eventually delivered.
    
    Attributes:
        base_delay: The base delay for message deliveries. Defaults to 1 second.
    """
    base_delay: SimTime = field(default_factory=lambda: simtime(seconds=1))

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.base_delay < self.min_delay:
            raise ValueError("Base delay must be at least as great as the minimum delay.")
    
    def arrival_time_for(self, sent_at: SimTime) -> SimTime:
        return SimTime(sent_at + self.min_delay + self.base_delay * (random.expovariate(lambd=2) + random.uniform(0, 1)))


@dataclass(frozen=True, kw_only=True)
class PartiallySynchronous(Synchronous):
    """Represents a partially synchronous system with eventual synchrony bounds.
    
    In a partially synchronous system, communication is eventually bounded after a
    global synchronization time (GST). Before GST, messages may experience
    unbounded delays; after GST, message delivery is bounded.
    
    Attributes:
        gst: The global synchronization time after which message bounds apply.
    """
    gst: SimTime

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.gst <= SIMTIME_EPSILON:
            raise ValueError("Global synchronization time (GST) must be a positive time.")
    
    def arrival_time_for(self, sent_at: SimTime) -> SimTime:
        if sent_at < self.gst:
            # If the message is sent before the global synchronization time (GST),
            match random.choice(["short", "long", "long", "long", "long", "near lost", "near lost", "lost", "lucky"]):
                case "short":
                    return SimTime(sent_at + simtime(nanoseconds=1) + self.fixed_delay * random.uniform(0, 2))
                case "long":
                    return SimTime(
                        sent_at
                        + SIMTIME_EPSILON
                        + self.fixed_delay
                            * (1 + random.uniform(0, 1) + random.expovariate(lambd=1/10))
                    )
                case "near lost":
                    return SimTime(
                        self.gst
                        + SIMTIME_EPSILON
                        + self.fixed_delay * (1_000_000 + random.expovariate(lambd=1/1_000_000))
                    )
                case "lost":
                    return SimTime(max(self.gst, self.gst + simtime(days=999_999)))
                case "lucky":
                    # occasionally, behave synchronously
                    return super().arrival_time_for(sent_at)
        else:
            return super().arrival_time_for(sent_at)


@dataclass(frozen=True)
class StochasticExponential(SynchronyModel):
    """Represents a stochastic system with exponentially distributed delays.
    
    In a stochastic system, message delivery times follow an exponential distribution.
    This models realistic network behavior with occasional long delays.
    
    Attributes:
        delta_t: The time scale parameter for the exponential distribution.
                 Defaults to 1 millisecond.
    """
    delta_t: SimTime = field(default=simtime(milliseconds=1))
    
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.delta_t < SIMTIME_EPSILON:
            raise ValueError("Delta time must be strictly positive.")
    
    def arrival_time_for(self, sent_at: SimTime) -> SimTime:
        return SimTime(sent_at + self.min_delay + self.delta_t * random.expovariate(lambd=1))


@dataclass(frozen=True)
class System:
    """Represents a distributed system with topology and synchrony model.
    
    A system combines a network topology (defining process connections) with a
    synchrony model (defining communication constraints).
    
    Attributes:
        topology: The network topology defining process connections.
        synchrony: The synchrony model defining communication constraints.
                   Defaults to Asynchronous.
    """
    topology: NetworkTopology
    synchrony: SynchronyModel = field(default_factory=Asynchronous)
    
    def processes(self) -> Iterable[Pid]:
        """Get all processes in the system.
        
        Returns:
            An iterable of all process identifiers in the system.
        """
        return self.topology.processes()

    def neighbors_of(self, pid: Pid) -> ProcessSet:
        """Get the neighboring processes of a given process.
        
        Args:
            pid: The identifier of the process.
        
        Returns:
            The set of process identifiers that are neighbors of the given process.
        """
        return self.topology.neighbors_of(pid)
