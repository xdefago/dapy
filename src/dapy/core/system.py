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
    def __post_init__(self):
        if self.min_delay < timedelta.resolution:
            raise ValueError("Minimum delay must be strictly positive.")
        
    @abstractmethod
    def arrival_time_for(self, sent_at: time) -> time:
        """
        Given a time when a message is sent, return the time when it should arrives.
        """

    
@dataclass(frozen=True)
class Synchronous(SynchronyModel):
    """
    Class to represent a synchronous system.
    All communication is bounded by a fixed time interval.
    """
    fixed_delay: timedelta = field(default=timedelta(milliseconds=1))
    
    def __post_init__(self):
        super().__post_init__()
        if self.fixed_delay < self.min_delay:
            raise ValueError("The fixed delay must be at least as great as the minimum delay.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        return sent_at + self.fixed_delay


@dataclass(frozen=True)
class Asynchronous(SynchronyModel):
    """
    Class to represent an asynchronous system.
    """
    base_delay: timedelta = field(default=timedelta(seconds=1))

    def __post_init__(self):
        super().__post_init__()
        if self.base_delay < self.min_delay:
            raise ValueError("Base delay must be at least as great as the minimum delay.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        return sent_at + self.min_delay + self.base_delay * (random.expovariate(lambd=2) + random.uniform(0, 1))


@dataclass(frozen=True, kw_only=True)
class PartiallySynchronous(Synchronous):
    """
    Class to represent a partially synchronous system.
    Communication is bounded by a fixed time interval, but not all processes are synchronized.
    """
    gst: time

    def __post_init__(self):
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
    """
    Class to represent a stochastic system.
    Communication is bounded by a random time interval.
    """
    delta_t: timedelta = field(default=timedelta(milliseconds=1))
    
    def __post_init__(self):
        super().__post_init__()
        if self.delta_t < timedelta.resolution:
            raise ValueError("Delta time must be strictly positive.")
    
    def arrival_time_for(self, sent_at: time) -> time:
        return sent_at + self.min_delay + self.delta_t * random.expovariate(lambd=1)


@dataclass(frozen=True)
class System:
    """
    Class to represent a system with a network topology and a set of processes.
    """
    topology: NetworkTopology
    synchrony: SynchronyModel = field(default_factory=Asynchronous)
    
    def processes(self) -> Iterable[Pid]:
        """
        Get the processes in the system.
        """
        return self.topology.processes()

    def neighbors_of(self, pid: Pid) -> ProcessSet:
        """
        Get the neighbors of a given process.
        """
        return self.topology.neighbors_of(pid)
