# CMake Caveats & Footguns

Issue-Key example: `Issue-Key: CMAKE-9a2dfe`.

## Golden CMake Patterns (Add-On)
- Prefer modern target-based commands: `target_sources`, `target_include_directories`, `target_link_libraries` with explicit scopes over global flags.
- Provide INTERFACE targets for header-only libs; export properties (include dirs/defines/compile features) through them.
- Centralize warnings and `-Werror` via an option (e.g., `MYPROJECT_ENABLE_WERROR`) defaulting ON in CI but optional locally; never apply to third-party targets.

## Common Footguns
- Switching generators on same build directory corrupts cache—use separate `build-<gen>` dirs.
- `CMAKE_TOOLCHAIN_FILE` must be set on first configure; later changes require cache wipe.
- `include_directories`/`link_libraries` at directory scope leak to all targets; avoid.
- FetchContent without pinned `GIT_TAG` leads to drift; lock versions and support offline mode.
- In-source builds pollute tree and cause accidental commits; guard against them.
- COMPONENT installs fail silently if targets lack COMPONENT—keep component names consistent.
