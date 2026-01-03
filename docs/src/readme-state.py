# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from dapy.core import State, ProcessSet, ChannelSet

#
# State of a process in the algorithm.
#
@dataclass(frozen=True)
class LearnState(State):
    neighbors_i: ProcessSet = field(default_factory=ProcessSet)
    proc_known_i: ProcessSet = field(default_factory=ProcessSet)
    channels_known_i: ChannelSet = field(default_factory=ChannelSet)
    part_i: bool = False
