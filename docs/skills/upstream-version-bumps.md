---
name: upstream-version-bumps
description: Preserve RPM release and rebuild-counter semantics when changing upstream versions.
metadata:
  type: procedure
---

# Upstream version bumps

When changing `tools/upstream_bump.py`, keep the spec version, source lock,
and source manifest together. A changed `Version:` resets the numeric leading
literal of `Release:` to `1`; preserve following macros and comments. Leave
macro-only releases (`%autorelease`, `%{baserelease}`, `%{samba_release}`)
alone because their expanded value cannot be inferred from the recipe.
A no-op version rewrite must preserve the release.

Retire the package's `dist_bump` entry when applying a new upstream version,
for both GNOME and forge feeds. Its baseline records only the release, so a
reset from `1` to `1` cannot invalidate it automatically: without removal the
new version inherits a rebuild counter that belongs to the old sources.
Preserve counters on same-version applications.

Cover these cases in `tests/test_upstream_bump.py`, including an unchanged
numeric release across a version bump and both feed paths. Use fake downloads
and scratch trees so validation does not depend on live upstream releases.
