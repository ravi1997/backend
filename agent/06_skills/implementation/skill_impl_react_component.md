# Skill: Implement React Component

## Context

When assigned to create a frontend component in a React/Next.js environment.

## 1. Analysis

- **Props**: Identify required props and types.
- **State**: Determine local state vs global state.
- **Styles**: Check styling approach (Tailwind, CSS Modules, Styled Components).

## 2. Scaffold (TypeScript)

```tsx
import React from 'react';

interface MyComponentProps {
  title: string;
  isActive?: boolean;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, isActive = false }) => {
  return (
    <div className={`component ${isActive ? 'active' : ''}`}>
      <h2>{title}</h2>
    </div>
  );
};
```

## 3. Implementation Steps

1. Define Interface.
2. Implement Render Logic.
3. Add Interactivity (Hooks).
4. Apply Styles.

## 4. Verification

- Does it render without crashing?
- Are PropTypes/Interfaces correct?
- Is it accessible?
