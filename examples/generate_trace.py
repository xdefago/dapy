# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Generate a sample trace file for testing the dapyview GUI."""

from pathlib import Path

from dapy.algo.learn import LearnGraphAlgorithm, Start
from dapy.core import Asynchronous, Pid, Ring, System
from dapy.sim import Settings, Simulator

# Enable trace collection
settings = Settings(enable_trace=True)

# Define a ring topology with 5 processes
system = System(
    topology=Ring.of_size(5),
    synchrony=Asynchronous(),
)

# Instantiate the algorithm
algorithm = LearnGraphAlgorithm(system)

# Create the simulator
sim = Simulator.from_system(system, algorithm, settings=settings)

# Run the simulation
sim.start()
sim.schedule(event=Start(target=Pid(1)))
sim.run_to_completion()
assert sim.trace is not None

# Save the trace to a pickle file
trace_file = Path(__file__).parent.parent / "traces" / "sample_trace.pkl"
trace_data = sim.trace.dump_pickle()
trace_file.write_bytes(trace_data)

print(f"Trace saved to: {trace_file}")
print(f"Events: {len(sim.trace.events_list)}")
print(f"Configurations: {len(sim.trace.history)}")
