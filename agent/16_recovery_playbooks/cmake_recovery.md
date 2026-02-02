# CMake Recovery Playbook

Map to hard cases HC-CMAKE-XXX. Issue-Key example: `Issue-Key: CMAKE-<hash>`.

## RECOVERY-CMAKE-001: Generator/Cache Problems
- Steps: inspect `CMakeCache.txt` for `CMAKE_GENERATOR`; if mismatch, remove build dir and reconfigure with `cmake -S . -B build -G <gen> [-DCMAKE_TOOLCHAIN_FILE=...]`.
- Validate: configure + build succeeds; generator logged correctly.

## RECOVERY-CMAKE-002: find_package/Dependency Failures
- Steps: run `cmake --find-package -DNAME=<Pkg> -DMODE=EXIST`; set `Pkg_DIR`/`CMAKE_PREFIX_PATH`; install missing dev packages; fix custom Find modules to emit imported targets.
- Validate: configure reruns clean; `ninja -C build` links successfully.

## RECOVERY-CMAKE-003: Link Scope & Include Issues
- Steps: replace global include/link flags with target-based `target_include_directories`/`target_link_libraries` scopes; ensure PUBLIC/INTERFACE where consumers need them; regenerate compile_commands.
- Validate: downstream target builds; headers resolved without manual flags.

## RECOVERY-CMAKE-004: FetchContent & Offline Builds
- Steps: pin `GIT_TAG`, set `FETCHCONTENT_FULLY_DISCONNECTED` with pre-populated sources; configure proxy if needed; add mirrors or vendored tarballs.
- Validate: configure works offline; version stable across CI/dev.

## RECOVERY-CMAKE-005: Install/Export/Package Failures
- Steps: include `GNUInstallDirs`; add install rules for targets/headers with COMPONENT; add `install(EXPORT ...)` with namespace and `configure_package_config_file`.
- Validate: `cmake --install build --prefix /tmp/pkg`; downstream sample `find_package` succeeds.

## RECOVERY-CMAKE-006: Cross-Compile & Toolchain Misuse
- Steps: ensure first configure includes `-DCMAKE_TOOLCHAIN_FILE`; set `CMAKE_SYSROOT` and find root path modes; adjust pkg-config paths; rebuild.
- Validate: compile commands show sysroot paths; binaries link against target libs only.

## RECOVERY-CMAKE-007: Warning/Custom Command Noise
- Steps: centralize warning flags with option `WERROR`; adjust custom commands to declare OUTPUT/DEPENDS/BYPRODUCTS; guard in-source build with fatal error.
- Validate: `ninja -C build` incremental builds cleanly without repeated commands; CI warnings resolved.
