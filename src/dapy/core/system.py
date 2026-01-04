# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import time, timedelta
from typing import Iterable

from .pid import Pid, ProcessSet
from .topology import NetworkTopology


@dataclass(frozen=True)
class SynchronyModel(ABC):
    min_delay: timedelta = field(default=timedelta.resolution)
    def __post_init__(self) -> None:
        if self.min_delay < timedelta.resolution:
            raise ValueError("Minimum delay must be strictly positive.")
        
    @abstractmethod
    def arrival_time_for(self, sent_at: time) -> time:
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
    fixed_delay: timedelta = field(default=timedelta(milliseconds=1))
    
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.fixed_delay < self.min_delay:
            raise ValueError("The fixed delay must be at least as great as the minimum delay.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        return sent_at + self.fixed_delay


@dataclass(frozen=True)
class Asynchronous(SynchronyModel):
    """Represents an asynchronous system with unbounded communication delays.
    
    In an asynchronous system, there are no bounds on message delivery times.
    Messages may be delayed arbitrarily but are eventually delivered.
    
    Attributes:
        base_delay: The base delay for message deliveries. Defaults to 1 second.
    """
    base_delay: timedelta = field(default=timedelta(seconds=1))

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.base_delay < self.min_delay:
            raise ValueError("Base delay must be at least as great as the minimum delay.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        return sent_at + self.min_delay + self.base_delay * (random.expovariate(lambd=2) + random.uniform(0, 1))


@dataclass(frozen=True, kw_only=True)
class PartiallySynchronous(Synchronous):
    """Represents a partially synchronous system with eventual synchrony bounds.
    
    In a partially synchronous system, communication is eventually bounded after a
    global synchronization time (GST). Before GST, messages may experience
    unbounded delays; after GST, message delivery is bounded.
    
    Attributes:
        gst: The global synchronization time after which message bounds apply.
    """
    gst: time

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.gst < timedelta.resolution:
            raise ValueError("Global synchronization time (GST) must be a positive time.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        if sent_at < self.gst:
            # If the message is sent before the global synchronization time (GST),
            match random.choice(["short", "long", "long", "long", "long", "near lost", "near lost", "lost", "lucky"]):
                case "short":
                    return sent_at + timedelta(microseconds=0.001) + self.fixed_delay * random.uniform(0, 2)
                case "long":
                    return (
                        sent_at
                        + timedelta(microseconds=0.001)
                        + self.fixed_delay
                            * (1 + random.uniform(0, 1) + random.expovariate(lambd=1/10))
                    )
                case "near lost":
                    return (
                        self.gst
                        + timedelta(microseconds=0.001)
                        + self.fixed_delay * (1_000_000 + random.expovariate(lambd=1/1_000_000))
                    )
                case "lost":
                    return max(self.gst, timedelta(days=999_999))
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
    delta_t: timedelta = field(default=timedelta(milliseconds=1))
    
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.delta_t < timedelta.resolution:
            raise ValueError("Delta time must be strictly positive.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        return sent_at + self.min_delay + self.delta_t * random.expovariate(lambd=1)


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
