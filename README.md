# DebateArena

AI-powered multi-agent debate arena.

## Installation

```bash
pip install -e .
```

## Usage

```python
from debate_arena import Arena

arena = Arena(
    topic="Should AI development be regulated?",
    rounds=3
)

result = arena.run()
print(result.report)
```

## Examples

See `examples/` directory for detailed examples.
