# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field

from dapy.core import Message, Pid, ProcessSet, Signal


#
# Messages and signals used in the algorithm.
#
@dataclass(frozen=True)
class PositionMsg(Message):
    origin: Pid
    neighbors: ProcessSet = field(default_factory=ProcessSet)

@dataclass(frozen=True)
class Start(Signal):
    pass

@dataclass(frozen=True)
class GraphIsKnown(Signal):
    """Event to signal that the graph is known."""
    pass
