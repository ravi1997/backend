# Decisions Log Template

## Snapshot Information

- **Snapshot ID**: [Timestamp: YYYY-MM-DD-HH-MM-SS]
- **Related Context Snapshot**: `CONTEXT_SNAPSHOT.md`
- **Session Start**: [YYYY-MM-DD HH:MM]

## Decision Log

### Decision 1: [Brief Title]

- **Decision ID**: DEC-[YYYYMMDD]-001
- **Category**: [ARCHITECTURE / IMPLEMENTATION / TOOLING / PROCESS / SECURITY / DEVOPS]
- **Date**: [YYYY-MM-DD HH:MM]
- **Risk Level**: [LOW / MEDIUM / HIGH / CRITICAL]

**Context**:
[What situation led to this decision? What problem was being solved?]

**Options Considered**:

1. **Option A**: [Description]
   - Pros: [List]
   - Cons: [List]
2. **Option B**: [Description]
   - Pros: [List]
   - Cons: [List]
3. **Option C**: [Description]
   - Pros: [List]
   - Cons: [List]

**Decision Made**:
[Which option was chosen]

**Rationale**:
[Why this option was selected over alternatives. Include specific reasoning.]

**Reversibility**:

- **Can Be Reversed**: [YES / NO / PARTIALLY]
- **Rollback Procedure**: [If reversible, how to undo]
- **Rollback Cost**: [Effort required to reverse]

**Impact**:

- **Affected Components**: [List of files, modules, or systems]
- **Breaking Changes**: [YES / NO - if yes, describe]
- **Migration Required**: [YES / NO - if yes, describe]

**Validation**:

- **How to Verify**: [How to confirm decision was correct]
- **Success Criteria**: [What indicates this was the right choice]

---

### Decision 2: [Brief Title]

- **Decision ID**: DEC-[YYYYMMDD]-002
- **Category**: [...]
- **Date**: [YYYY-MM-DD HH:MM]
- **Risk Level**: [...]

[Repeat structure above for each decision]

---

## Token Budget Decisions

### Model Switching

- **Switch Attempted**: [YES / NO]
- **Switch Date**: [YYYY-MM-DD HH:MM]
- **From Model**: [Model name]
- **To Model**: [Model name]
- **Reason**: [Why switch was needed]
- **Result**: [SUCCESS / FAILED / NOT_SUPPORTED]
- **Context Preserved**: [YES / NO / PARTIAL]

### Context Management

- **Context Diet Applied**: [YES / NO]
- **Date**: [YYYY-MM-DD HH:MM]
- **Components Unloaded**: [List]
- **Rationale**: [Why these components were removed]

- **Least-Token Mode Activated**: [YES / NO]
- **Date**: [YYYY-MM-DD HH:MM]
- **Impact**: [How it affected work]

### Chunking Strategy

- **Chunking Applied**: [YES / NO]
- **Output Type**: [Code / Documentation / Data]
- **Chunk Count**: [Number]
- **Chunk Strategy**: [By file / By feature / By size / Other]

## Stack and Tooling Decisions

### Stack Selection

- **Primary Stack**: [e.g., Python, Node, C++]
- **Rationale**: [Why this stack]
- **Alternatives Considered**: [Other stacks evaluated]

### Library/Framework Choices

| Decision | Chosen | Alternative(s) | Rationale |
| --- | --- | --- | --- |
| [Category] | [Library/Framework] | [Alternatives] | [Why chosen] |
| [Category] | [Library/Framework] | [Alternatives] | [Why chosen] |

### DevOps Decisions

- **CI/CD Platform**: [e.g., GitHub Actions]
- **Containerization**: [Docker / None]
- **Deployment Strategy**: [e.g., Blue-Green, Rolling]
- **Rationale**: [Why these choices]

## Architecture Decisions

### Design Patterns

- **Pattern**: [e.g., MVC, Microservices, Monolith]
- **Rationale**: [Why this pattern]
- **Trade-offs**: [What was sacrificed]

### Data Models

- **Schema Decisions**: [Key schema choices]
- **Rationale**: [Why structured this way]
- **Migration Path**: [How to evolve schema]

## Security and Compliance Decisions

### Security Measures

- **Authentication**: [Method chosen]
- **Authorization**: [Approach]
- **Data Protection**: [Encryption, hashing, etc.]
- **Rationale**: [Why these measures]

### Compliance

- **Standards**: [e.g., GDPR, HIPAA, SOC2]
- **Implementation**: [How compliance is achieved]

## Process and Workflow Decisions

### Development Process

- **Branching Strategy**: [e.g., Git Flow, Trunk-based]
- **Review Process**: [PR requirements]
- **Testing Strategy**: [Unit, Integration, E2E coverage]

### Quality Gates

- **Gates Applied**: [List of gates]
- **Rationale**: [Why these gates]
- **Exceptions**: [Any gates skipped and why]

## Deferred Decisions

### Decisions Postponed

1. **Decision**: [What needs to be decided]
   - **Reason for Deferral**: [Why not decided now]
   - **Deadline**: [When decision must be made]
   - **Blocker**: [What information is needed]

2. **Decision**: [...]
   - **Reason for Deferral**: [...]
   - **Deadline**: [...]
   - **Blocker**: [...]

## Decision Impact Summary

### High-Impact Decisions

[List of decisions with HIGH or CRITICAL risk level]

1. [Decision ID]: [Brief description]
2. [Decision ID]: [Brief description]

### Irreversible Decisions

[List of decisions that cannot be easily undone]

1. [Decision ID]: [Brief description and why irreversible]
2. [Decision ID]: [Brief description and why irreversible]

## Verification Checklist

- [ ] All major decisions documented
- [ ] Rationale provided for each decision
- [ ] Reversibility assessed for each decision
- [ ] Risk levels assigned
- [ ] Token budget decisions captured
- [ ] No placeholder text remains

## Related Files

- `plans/Continuity/CONTEXT_SNAPSHOT.md`
- `plans/Continuity/PROGRESS.md`
- `plans/Continuity/NEXT.md`
- `agent/00_system/03_decision_policy.md`
- `agent/00_system/12_token_budget_and_model_switching.md`
