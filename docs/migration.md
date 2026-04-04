# Migration from `tsdecomp`

## Imports

New code should use:

```python
from detime import DecompositionConfig, decompose
```

Legacy code may continue to import `tsdecomp` for one deprecation cycle, but it
now emits a warning and resolves to the same De-Time implementation.

## CLI

Preferred commands:

- `detime run`
- `detime batch`
- `detime profile`
- `detime version`

Legacy `tsdecomp` CLI aliases still work with a deprecation notice.

## Removed modules and methods

The following are no longer part of the main package:

- `bench_config`
- `leaderboard`
- `DR_TS_REG`
- `DR_TS_AE`
- `SL_LIB`

These moved to the companion benchmark repository `de-time-bench`.
