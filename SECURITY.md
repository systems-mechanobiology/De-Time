# Security Policy

## Scope

De-Time is a standalone open-source research software library for time-series
decomposition. It is primarily a Python package and CLI, not a hosted service.
Security reports are still important when they affect:

- package installation or dependency safety,
- arbitrary file read or write behavior through the CLI or library,
- unsafe deserialization or command execution paths,
- native extension build or runtime memory-safety issues,
- disclosure of private data through logs, saved artifacts, or reports.

Issues that are usually not treated as security vulnerabilities for this
project include:

- incorrect decomposition results without a security impact,
- benchmark regressions,
- numerical instability without confidentiality, integrity, or availability
  impact,
- documentation mistakes or weak defaults that are not exploitable.

## Supported versions

Because the project is still in an early standalone phase, security fixes are
generally applied on:

- the latest release in the `0.1.x` line,
- the current default branch, when a fix has not yet been released.

Older experimental snapshots, archived benchmark artifacts, and unpublished
local branches should not be assumed to receive security fixes.

## Reporting a vulnerability

Please do **not** open a public issue for a suspected exploitable security
problem.

Use one of these paths instead:

1. Open a private GitHub security advisory if the repository has that feature
   enabled.
2. Otherwise contact the maintainer through the repository owner profile or the
   maintainer contact channel listed in the project metadata.
3. If neither is available, open a minimal issue that requests a private
   contact path **without** including exploit details or proof-of-concept code.

When reporting, include:

- affected version or commit,
- operating system and Python version,
- whether the issue affects the Python path, CLI path, native extension, or
  packaging path,
- reproduction steps,
- expected impact,
- whether the issue depends on optional third-party backends.

## Response expectations

Best-effort targets for initial triage are:

- acknowledgment within 7 days,
- a decision on severity and scope within 14 days when reproduction is clear,
- coordinated disclosure after a fix or mitigation is ready.

These are goals rather than contractual guarantees, especially for an
academically maintained open-source project.

## Disclosure policy

The project prefers coordinated disclosure:

- keep exploitable details private until a fix or mitigation is available,
- publish a changelog note or release note when the fix ships,
- credit reporters when they want attribution.

## Dependency and supply-chain notes

De-Time depends on the scientific Python ecosystem and some optional
third-party backends. Security hardening therefore includes:

- keeping packaging metadata explicit,
- preferring reproducible wheel-first installation paths where possible,
- failing clearly when optional dependencies are unavailable or unsupported,
- avoiding undocumented network behavior in the library and CLI.

Users running the package in sensitive environments should:

- pin dependencies,
- review optional extras before installation,
- prefer isolated virtual environments,
- validate artifacts before distributing them to downstream systems.
