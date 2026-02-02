# Example: Release

## Scenario

Project "MegaTool" is ready for v1.0.0.

## Steps

1. **Verification**: `gate_global_release.md` runs. 100% pass.
2. **Docs**: `plans/Release/RELEASE_NOTES_V1.md` created.
3. **Git**: `git tag -a v1.0.0 -m "First production release"`.
4. **Packaging**: `npm pack` generates the tarball.
5. **State**: `RELEASE_STATE.md` updated with new version and milestone 100% completion.
