# Rules: Next.js

**Scope**: Next.js Framework Specifics (App Router / Pages Router).

## 1. Routing

- **App Router**: Prefer App Router (`app/`) for new projects.
- **Server Components**: Use Server Components (RSC) by default. Add `'use client'` only when interactivity is needed.

## 2. Data Fetching

- **Fetch**: Use `fetch` API with caching options (`force-cache`, `no-store`).
- **Server Actions**: Use Server Actions for mutations instead of API routes where appropriate.

## 3. Optimization

- **Images**: Mandatory usage of `<Image />` component.
- **Fonts**: Use `next/font`.
- **Scripts**: Use `<Script />` with appropriate loading strategy.

## 4. Configuration

- **Next Config**: Keep `next.config.js` clean.
- **Environment**: Public variables in `.env` must be prefixed `NEXT_PUBLIC_`.

## 5. SEO

- **Metadata**: Use the Metadata API for head tags.
