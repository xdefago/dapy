"""Test loading the trace file."""

import sys
from dapy.sim import Trace
from pathlib import Path

trace_file = Path('examples/sample_trace.json')
print(f'Loading: {trace_file}')
print(f'File exists: {trace_file.exists()}')

if not trace_file.exists():
    print('ERROR: File does not exist!')
    sys.exit(1)

print(f'File size: {trace_file.stat().st_size} bytes')

try:
    content = trace_file.read_text()
    print(f'Content length: {len(content)} characters')
    print(f'\nFirst 500 chars:')
    print(content[:500])
    print(f'\n\nAttempting to load JSON...')
    trace = Trace.load_json(content)
    print(f'\n✓ Success! Loaded trace with {len(trace.events_list)} events')
    print(f'  History entries: {len(trace.history)}')
except Exception as e:
    print(f'\n✗ Error: {e}')
    print(f'\nException type: {type(e).__name__}')
    import traceback
    print('\nFull traceback:')
    traceback.print_exc()
    sys.exit(1)
