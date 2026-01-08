# Toolchain Managment

This directory contains policies and templates for managing runtime versions across the monorepo.

## Contents

-   **`TOOLCHAIN_POLICY.md`**: Definitive rules for version pinning and resolution.
-   **`templates/`**: Standard pin files (`.tool-versions`, `.nvmrc`, etc.) to copy into components.

## Quick Start

1.  **Check Policy**: Read `TOOLCHAIN_POLICY.md`.
2.  **Pin Version**: Copy a template to your component root.
    ```bash
    cp agent/toolchains/templates/.nvmrc backend/api/
    ```
3.  **Verify**: Ensure your workflow defines a check against these files.
