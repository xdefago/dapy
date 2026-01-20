# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from datetime import timedelta

from dapy.algo.learn import LearnGraphAlgorithm, Start
from dapy.core import Asynchronous, Pid, Ring, System
from dapy.sim import Settings, Simulator

# This example demonstrates how to use the dapy library to simulate a distributed algorithm
# This runs a system of 4 processes in a ring topology emulating an asynchronous model, to execute
# the learn graph algorithm.

#
# optionally define settings (e.g. enable trace)
#
settings = Settings(enable_trace=True)

#
# define the system
# - topology: Ring of 4 processes
# - synchrony model: Asynchronous
#
system = System(
    topology=Ring.of_size(4),
    synchrony=Asynchronous(),
)
print("System:")
print(system)

#
# Instantiate the learn graph algorithm with the system
#
algorithm = LearnGraphAlgorithm(system)
print("Algorithm:", algorithm.name)
print(algorithm)

#
# Create the simulator environment using
# - the system
# - the algorithm
# - the settings
#
sim = Simulator.from_system(system, algorithm, settings=settings)

# Start the simulation; all processes are initialized to their initial state 
sim.start()
# Schedule some initial event to start the algorithm (here we start process 1)
sim.schedule(event=Start(target=Pid(1)))
# Run the algorithm until completion
# - this will run the algorithm until the system has no pending events (one can specify a step limit)
sim.run_to_completion()

#
# Display the execution based on the trace
#

# Display the configurations
print("\n----[ Trace ]---- configuration history")
for event in sim.trace.history:
    time = event.time
    event = event.configuration
    print(f"{time} {event}")
    
# Display the events
print("\n----[ Trace ]---- events")
for timed_event in sim.trace.events_list:
    start = timed_event.start
    end = timed_event.end
    event = timed_event.event
    print(f"{start} {end} {event}")

# compare changes between consecutive configurations
print("\n----[ Trace ]---- changes")
for i in range(len(sim.trace.history)-1):
    for p in sim.trace.history[i+1].configuration.changed_from(sim.trace.history[i].configuration):
        print(f"+++ Process {p} changed from config {i} to {i+1}")

#
# NOTE:
# Timestamps such as `0:00:03.602244` indicate the time elapsed since the beginning of the simulated execution.
# The time does not refer to any real time, but to the simulation time (virtual time in the simulated environment).
# Communication delays are defined randomly based on the model.
# The format is `hour:minute:second.decimals`.
#
