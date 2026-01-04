# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Generate a sample trace file for testing the dapyview GUI."""

from dapy.core import Pid, System, Ring, Asynchronous
from dapy.algo.learn import LearnGraphAlgorithm, Start
from dapy.sim import Simulator, Settings
from datetime import timedelta
from pathlib import Path

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
sim.schedule_event(timedelta(seconds=0), Start(target=Pid(1)))
sim.run_to_completion()
assert sim.trace is not None

# Save the trace to a JSON file
trace_file = Path(__file__).parent.parent / "traces" / "sample_trace.json"
trace_json = sim.trace.dump_json()
trace_file.write_text(trace_json)

print(f"Trace saved to: {trace_file}")
print(f"Events: {len(sim.trace.events_list)}")
print(f"Configurations: {len(sim.trace.history)}")
