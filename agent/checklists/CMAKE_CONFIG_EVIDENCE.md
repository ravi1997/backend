# CHECKLIST: CMake Configuration Evidence

**Purpose:** Gather evidence for failures during the CMake generation phase.
**Source:** `checklists/CMAKE_CONFIG_EVIDENCE.md`

## 1. Environment & Setup
- [ ] CMake version (`cmake --version`)
- [ ] Generator used (`-G` flag or default)
- [ ] Build directory path (is it in-source or out-of-source?)

## 2. Dependency Discovery
- [ ] Review `find_package` results in the log
- [ ] Check `CMAKE_PREFIX_PATH` or `PKG_CONFIG_PATH`
- [ ] Verify if environment variables like `PATH` or `LD_LIBRARY_PATH` are set correctly

## 3. CMake Logs
- [ ] Inspect `CMakeFiles/CMakeError.log`
- [ ] Inspect `CMakeFiles/CMakeOutput.log`
- [ ] Check for "Check for working C compiler" failures

## 4. Cache & Input
- [ ] List variables passed via `-D` flags
- [ ] Identify if `CMakeLists.txt` uses `FetchContent` or `ExternalProject`
- [ ] Check if `submodules` are initialized if they contain dependencies

## 5. Metadata for Agent
- [ ] `FLOW:CMAKE_CONFIG_DEBUG`
- [ ] `STAGE:GENERATION`
- [ ] `TOOL:CMAKE`
