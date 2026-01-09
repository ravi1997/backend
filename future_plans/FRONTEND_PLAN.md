# Frontend Implementation Plan

## 1. Technology Stack
- **Framework**: [Next.js](https://nextjs.org/) (React) - For server-side rendering, routing, and performance.
- **Language**: TypeScript - For type safety and better developer experience.
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) - For rapid, utility-first styling.
- **UI Components**:
  - [Shadcn UI](https://ui.shadcn.com/) (based on Radix UI) - For accessible, customizable components.
  - [Lucide React](https://lucide.dev/) - For icons.
- **State Management**:
  - Server State: [TanStack Query](https://tanstack.com/query/latest) (React Query) - For caching and synchronizing API data.
  - Client State: [Zustand](https://github.com/pmndrs/zustand) - For lightweight global state (e.g., auth, form builder draft).
- **Form Handling**:
  - [React Hook Form](https://react-hook-form.com/) - For efficient form validation and management.
  - [Zod](https://zod.dev/) - For schema validation (syncs with backend schemas).
- **Drag & Drop**: [Dnd Kit](https://dndkit.com/) - For the drag-and-drop form builder interface.
- **Charts/Analytics**: [Recharts](https://recharts.org/) or [Visx](https://airbnb.io/visx/).

---

## 2. Project Structure
```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/             # Authentication routes (login, register)
│   ├── (dashboard)/        # Main dashboard layout
│   │   ├── forms/          # Form management
│   │   ├── responses/      # Response viewer
│   │   ├── analytics/      # Global analytics
│   │   └── settings/       # User/Org settings
│   ├── builder/            # Form Builder (separate layout)
│   │   └── [formId]/       # Edit specific form
│   └── submit/             # Public form submission pages
│       └── [slug]/         # Dynamic route for forms
├── components/
│   ├── ui/                 # Reusable atomic components (Button, Input, Card)
│   ├── form-builder/       # Builder-specific components (DraggableField, PropertiesPanel)
│   ├── dashboard/          # Dashboard widgets (StatsCard, FormList)
│   └── layout/             # Sidebar, Header, Footer
├── lib/
│   ├── api.ts              # Axios/Fetch wrapper with interceptors
│   ├── utils.ts            # Helper functions
│   └── constants.ts        # App-wide constants
├── hooks/                  # Custom React hooks (useAuth, useFormBuilder)
├── store/                  # Zustand stores
├── types/                  # TypeScript interfaces (IForm, IUser, IResponse)
└── styles/                 # Global styles
```

---

## 3. Core Modules & Features

### A. Authentication & User Management
- **Pages**: Login, Register, Forgot Password, Profile Settings.
- **Features**:
  - JWT storage (HttpOnly cookies preferred or local storage with interceptors).
  - Protected routes (Middleware).
  - Role-based access control (Admin vs. User vs. Manager views).

### B. Dashboard
- **Overview**:
  - Summary cards (Total Forms, Responses, Active Forms).
  - Recent activity feed.
- **Form Management**:
  - List view with filtering/searching.
  - Create new form (from scratch, template, or AI).
  - Form actions: Edit, Preview, Share, Clone, Delete.

### C. Advanced Form Builder (The Core)
- **Interface**:
  - **Left Panel**: Component Library (Input, Select, Rating, File Upload, etc.).
  - **Center Canvas**: Interactive Drag & Drop area. Live preview of the form.
  - **Right Panel**: Properties Editor (Label, Validation, Logic, Styling).
- **Features**:
  - **Logic Builder**: UI for defining "If [Unit] is [Mobile], show [Operating System]".
  - **Validation**: visual configuration for required, regex, min/max.
  - **Multi-step/Section support**: Tabs to manage `sections` in the backend model.
  - **Version Control**: Dropdown to switch/view previous versions.

### D. Public Submission Interface
- **Design**: Clean, distraction-free, mobile-responsive layout.
- **Performance**: Static Generation (SSG) or Incremental Static Regeneration (ISR) for high-traffic forms.
- **Features**:
  - Real-time validation.
  - Auto-save drafts (local storage).
  - CAPTCHA integration (if required).
  - Success/Thank you pages with custom messages.

### E. Response Management & Analytics
- **Data Table**:
  - Advanced table with sorting, filtering, and pagination.
  - Custom column visibility.
  - Bulk actions (Delete, Export CSV/JSON).
- **Individual View**:
  - Detailed view of a single submission.
  - **Approval Workflow**: Buttons to Approve/Reject with comment history.
  - PDF Export of individual response.
- **Analytics Dashboard**:
  - Charts: Submission trends over time (Line), Device breakdown (Pie), completion rates.
  - AI Insights: Summary of text responses (Sentiment analysis results).

---

## 4. API Integration Strategy
- **Client**: `Axios` instance configured with `baseURL`.
- **Interceptors**:
  - **Request**: Attach `Authorization: Bearer <token>`.
  - **Response**: Handle global errors (401 -> Redirect to login, 403 -> Show "Access Denied").
- **Data Fetching**:
  - Use `React Query` hooks for all GET requests (`useForms`, `useFormDetails`).
  - Use `useMutation` for POST/PUT/DELETE actions.
  - Optimistic updates for better UI responsiveness (e.g., toggling a "favorite" star).

---

## 5. UI/UX Design System
- **Theme**: Support Light/Dark mode (system default).
- **Color Palette**:
  - Primary: Deep Indigo/Blue (Trust, Professional).
  - Secondary: Teal/Emerald (Success, Action).
  - Distructive: Rose/Red (Errors, Deletes).
- **Accessibility**:
  - Fully keyboard navigatable.
  - ARIA labels for all interactive elements.
  - Color contrast compliance (WCAG AA).

---

## 6. Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- Setup Next.js, Tailwind, Shadcn UI.
- Implement Auth (Login/Register) & API Interceptors.
- integrated with Backend `/auth` endpoints.

### Phase 2: Form Builder MVP (Weeks 3-4)
- Drag and Drop interface setup.
- Basic field types (Text, Number, Select).
- Save Form (`POST /forms`) & Update Form (`PUT /forms/{id}`).

### Phase 3: Public View & Submission (Week 5)
- Public route rendering based on JSON schema.
- Submission logic (`POST /forms/{id}/responses`).
- Validation handling.

### Phase 4: Dashboard & Responses (Week 6)
- List views for Forms and Responses.
- Response Table with export.
- Logic & Conditionals implementation in Builder.

### Phase 5: Advanced Features (Week 7+)
- Approval Workflows UI.
- Analytics Charts.
- AI Generation Interface (Prompt -> Form Json).
