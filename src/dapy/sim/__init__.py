# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""
dapy.sim

This module defines the runtime environment for simulating distributed algorithms.

The main components of this module include:
- `.simulator.Simulator`: The main class that runs a simulation according to a given system model and an algorithm.
- `.configuration.Configuration`: Represents the state of a system. This is a collection of the state of each process.
- `.trace.Trace`: When tracing is enabled, this class stores the entire history of the simulation.

In addition, the module provides a set of utility classes and functions to facilitate the simulation process, including:
- `.settings.Settings`: Configuration settings for the simulation.
- `.timed.TimedEvent`: Represents an event associated with a scheduled time.
- `.timed.TimedConfiguration`: Represents a configuration with a creation time.


"""

# re-exports
from .configuration import Configuration as Configuration
from .settings import Settings as Settings
from .simulator import Simulator as Simulator
from .timed import TimedConfiguration as TimedConfiguration
from .timed import TimedEvent as TimedEvent
from .trace import Trace as Trace
