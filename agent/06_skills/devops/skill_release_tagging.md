# Skill: Release Tagging Safety

## Purpose

Enforces a standardized and safe Git tagging procedure to ensure release traceability.

## Input Contract

- **Version ID**: e.g., `v1.2.3`.
- **Target Commit**: SHA or branch name.
- **Release Notes**: Summary of changes for the tag message.

## Execution Procedure

1. **Tag Validation**:
    - Verify the version follows `vX.Y.Z` format.
    - Check if the tag already exists: `git tag -l $VERSION`.
2. **State Sync**:
    - Ensure `agent/09_state/RELEASE_STATE.md` is updated with the candidate version.
3. **Local Creation**:
    - Run `git tag -a $VERSION -m "$RELEASE_NOTES"`.
4. **Verification**:
    - Run `git show $VERSION` to verify the metadata and commit tie.
5. **Push**:
    - Run `git push origin $VERSION`.

## Failure Modes

- **Tag Collision**: If the tag exists but points to a different commit, STOP and request a version bump.
- **Uncommitted Changes**: Refuse to tag if the working tree is dirty.

## Output Contract

- **Success Signal**: Tag pushed to remote.
- **Log Entry**: Update `agent/09_state/PROJECT_STATE.md` with the new tag reference.
