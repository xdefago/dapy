# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""
Project: dapy

This package provides a set of tools for prototyping distributed algorithms.

The project is structures into three main modules:
- `.core`: Contains the core components of the library, providing the basis for
    defining distributed algorithms and representing distributed executions.
- `.algo`: Contains implementations of various distributed algorithms, showcasing
    the capabilities of the library.
- `.sim`: Contains a simulation framework, allowing users to simulate and analyze the
    behavior of distributed algorithms.

Using this library consists of two main steps:
1. Defining a distributed algorithm using the core components.
2. Simulating the algorithm using the simulation framework.
"""

from . import core
from . import algo
from . import sim

__all__ = ['algo', 'core', 'sim']
