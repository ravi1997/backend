# Example: Token Safety Mode & Continuity

## Scenario

**Goal**: Implement a complex "User Dashboard" feature in a Next.js app.
**Constraint**: The Agent is approaching the token limit (75% used) midway through the task.
**Platform**: Does NOT support mid-session model switching.

---

## 1. Trigger Recognition

**Agent Internal Monologue**:
> "I have completed the API routes, but still need to build 4 frontend components. My token usage is now at 76% (ORANGE level). I cannot finish all components in this single turn without risking cutoff. I must activate Token Safety Mode."

**Action**:

- Switch to **ORANGE** protocol.
- Initiate **Continuity Snapshot**.

---

## 2. Snapshot Creation

**Command**:
`write_to_file("plans/Continuity/CONTEXT_SNAPSHOT.md", ...)`

**Content**:

```markdown
# Context Snapshot
**Level**: ORANGE
**Task**: Feature T-104 (User Dashboard)
**Stack**: Next.js, TypeScript, Tailwind
**Completed**: API Routes (/api/user/stats)
**Remaining**: DashboardCard, RecentActivity, Layout
```

**Command**:
`write_to_file("plans/Continuity/PROGRESS.md", ...)`

**Content**:

```markdown
## Completed Steps
1. Validated SRS.
2. Created API endpoints.
3. Wrote unit tests for API.

## Current Status
- API is passing tests.
- Frontend components are pending.
```

---

## 3. Least-Token Mode & Chunking

**Strategy**:
Instead of generating all 4 components in one massive response, the Agent breaks it down.

**Agent Output to User**:

```markdown
## Token Safety Status
**Level**: ORANGE (76%)
**Snapshot**: Saved to `plans/Continuity/`

I am switching to incremental generation to ensure safety.

### Chunk 1: Dashboard Layout
Generating `components/DashboardLayout.tsx`...
```

**Action**:

- Writes `DashboardLayout.tsx` to disk.
- Updates `plans/Continuity/PROGRESS.md` ("Layout Complete").

**Agent Output to User**:

```markdown
### Chunk 2: Dashboard Card
Generating `components/DashboardCard.tsx`...
```

**Action**:

- Writes `DashboardCard.tsx` to disk.
- Updates `plans/Continuity/PROGRESS.md` ("Card Complete").

---

## 4. Unexpected Limit Reach (RED Level)

**Situation**:
After Chunk 2, token usage spikes to 88% (RED).

**Agent Internal Monologue**:
> "I am now in RED. Model switching is unavailable. I have two components left. It is unsafe to continue. I must perform a graceful handoff."

**Action**:

- Finalize `plans/Continuity/NEXT.md`.

**Content of NEXT.md**:

```markdown
## Immediate Actions
1. Generate `RecentActivity.tsx`.
2. Generate `UserStats.tsx`.
3. Integrate components into `page.tsx`.
```

---

## 5. Graceful Handoff

**Final Agent Response**:

```markdown
## Token Safety Status
**Level**: RED (88%)
**Action**: Graceful Handoff

I have successfully implemented the API, Layout, and Card component. 

Due to token budget constraints, I am pausing here to prevent data loss. 

**To Resume:**
1. Start a new session.
2. Tell the new Agent: "Resume from `plans/Continuity/CONTEXT_SNAPSHOT.md`".
3. It will see that `RecentActivity.tsx` is the next step.
```

## 6. Recovery (New Session)

**New Agent Actions**:

1. User provides prompt: "Resume from `plans/Continuity/CONTEXT_SNAPSHOT.md`"
2. Agent reads `plans/Continuity/CONTEXT_SNAPSHOT.md`.
3. Agent reads `plans/Continuity/PROGRESS.md` -> Sees API/Layout/Card are done.
4. Agent reads `plans/Continuity/NEXT.md` -> Sees `RecentActivity.tsx` is next.
5. Agent immediately starts implementing `RecentActivity.tsx` without needing re-explanation.
