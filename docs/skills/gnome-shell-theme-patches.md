---
name: gnome-shell-theme-patches
description: >-
  Carry and verify GNOME Shell theme fixes in the package recipe.
metadata:
  type: procedure
---

# GNOME Shell theme patches

For a theme regression, check the Sass in the release locked by
`config/upstream-sources.json`. Carry the fix beside the other patches in
`packages/gnome-shell/` and register it with `Patch:` in the spec;
`%autosetup -S git` applies the registered patches. Preserve the imported
provenance in `.hummingbird-upstream.json`.

Nested Sass direction selectors need `&:ltr` and `&:rtl` when the rule must
style the parent widget itself. Bare `:ltr` and `:rtl` target descendants.
For the password entry, this distinction determines whether its content
reserves space for the submit button and avoids overlapping the reveal icon
([issue #289](https://github.com/projectbluefin/utah-packages/issues/289)).

Verify patches apply to the locked source and inspect both direction rules.
Package builds belong in the pinned GitHub Actions environment described in
the [contribution guide](../contributing.md#execution-environment). Visual
acceptance needs the rebuilt package in a GNOME session: check both the lock
screen and initial login, in left-to-right and right-to-left layouts, with the
password entry focused and the reveal and submit controls visible. Source
checks alone do not establish that the controls render without overlap.
