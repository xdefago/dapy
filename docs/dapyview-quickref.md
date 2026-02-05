---
layout: default
title: Quick Reference
parent: Dapyview
nav_order: 3
---

# Dapyview Quick Reference

## Launch

```bash
dapyview               # Open file selector
dapyview trace.pkl     # Open specific file
```

## Time Modes

| Mode | Description |
|------|-------------|
| **Physical Time** | Events by real simulation time |
| **Logical Time** | Events by Lamport clock (causality) |

Toggle: **Logical Time** checkbox in toolbar

## Color Scheme

### Without Selection

| Color | Type | Description |
|-------|------|-------------|
| ⚫ Black | Send/Receive | Sending or receiving message |
| ⚫ Gray | Local | Internal event |

### With Selection (Causality)

| Color | Relationship |
|-------|-------------|
| 🔴 Red | Selected event |
| 🔵 Light Blue | Causal past (happened-before) |
| 🟠 Light Orange | Causal future (happens-after) |
| ⚫ Black/Gray | Concurrent (not causally related) |

## Controls

### Mouse

| Action | Effect |
|--------|--------|
| Click event | Show causality |
| Click canvas | Clear selection |
| Scroll wheel | Zoom in/out |
| Click minimap | Navigate |

### Keyboard

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open trace |
| Ctrl+W | Close window |
| Ctrl+Q | Quit |
| Esc | Clear selection |

## Toolbar

| Control | Function |
|---------|----------|
| **Logical Time** checkbox | Toggle time mode |
| **Zoom** slider | Adjust horizontal scale (10%-500%) |
| **Add Ruler** button | Insert vertical measurement line |

## Navigation

- **Minimap**: Top-right corner shows network topology (drag to reposition)
- **Zoom**: Mouse wheel or slider
- **Rulers**: Click "Add Ruler", then drag to position

## Understanding the Diagram

```
p1  ─────○───○───────●─────────→  (Process timeline)
         │   │       │
         │   │       ↓ (Message)
p2  ─────○───○───────○─────────→
```

- **Horizontal lines**: Process timelines
- **Circles**: Events
- **Arrows**: Messages (send → receive)
- **Vertical rulers**: Time measurements

## Causality Rules

- **Direct message**: send → receive (blue to orange)
- **Same process**: earlier → later (blue to orange)
- **Transitivity**: If A→B and B→C, then A→C
- **Concurrent**: No causal relationship (default colors)

## Quick Tips

1. **Click any event** to see what influenced it (past) and what it influenced (future)
2. **Use logical time** to see causality without timing concerns
3. **Add rulers** to measure intervals between events
4. **Use minimap** to navigate large traces
5. **Open multiple windows** to compare different executions

## Common Tasks

### Find what caused an event
1. Click the event (turns red)
2. Look at light blue events (causal past)
3. Follow message arrows backward

### Check message ordering
1. Switch to logical time mode
2. Look at receive events on same process
3. Check logical clock values increase

### Measure delays
1. Click "Add Ruler" twice
2. Drag rulers to events
3. Read time difference on axis

### Compare executions
1. File → Open Trace (opens new window)
2. Arrange windows side-by-side
3. Compare event patterns

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Events overlap | Zoom in or use logical time |
| Can't find event | Use minimap or zoom out |
| Colors confusing | Click elsewhere to clear |
| Trace won't open | Check it's valid JSON from dapy |

## Getting Help

- **Full Guide**: `docs/dapyview-guide.md`
- **Packaging**: `docs/dapyview-packaging.md`
- **Issues**: https://github.com/xdefago/dapy/issues
- **Docs**: https://xdefago.github.io/dapy
