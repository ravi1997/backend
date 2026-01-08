# Skill: Flutter Linting & Formatting

**Purpose**: Ensure Flutter/Dart code follows analysis options.

## 1. Formatting
**Command**: `dart format .`
-   Apply strict line length (usually 80 or 120).

## 2. Linting
**Command**: `flutter analyze`
-   Reads `analysis_options.yaml`.
-   **Strictness**: Do not ignore warnings unless necessary.

## 3. Fixing Issues
-   **Quick Fixes**: `dart fix --apply`
-   **Manual**: Review `flutter analyze` output and fix errors.
