# CHECKLIST: C++ Build Failure Evidence

**Purpose:** Systematically collect evidence for C++ build failures (compilation or linking).
**Source:** `checklists/CPP_BUILD_EVIDENCE.md`

## 1. Environment Verification
- [ ] Record Compiler and Version (`g++ --version`, `clang++ --version`, or `cl.exe`)
- [ ] Record Build System Version (`cmake --version`, `make --version`, `ninja --version`)
- [ ] Record OS and Architecture (`uname -a`)

## 2. Build Output Collection
- [ ] Capture full stdout/stderr of the build command
- [ ] Identify the FIRST error in the log (often the root cause)
- [ ] Capture the specific compiler command that failed (if using `make VERBOSE=1` or `ninja -v`)

## 3. Configuration State
- [ ] Check `CMakeCache.txt` for suspicious variable values
- [ ] Verify if `include` directories exist and are correctly specified
- [ ] Check if required libraries (`.so`, `.a`, `.lib`) are found by the linker

## 4. Source Investigation
- [ ] Locating the line reported in the error
- [ ] Checking for missing headers (`#include`)
- [ ] Checking for syntax errors or C++ standard mismatches (e.g., using C++20 features with C++11 compiler)

## 5. Metadata for Agent
- [ ] `PROJECT_TYPE`: C++
- [ ] `BUILD_SYSTEM`: [cmake/make/ninja/msbuild]
- [ ] `ERROR_CATEGORY`: [compilation/linking/configuration]
