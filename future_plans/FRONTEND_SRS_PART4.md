# Frontend SRS - Part 4: Error Handling, Testing & Non-Functionals (Sections 5, 8, 13-14)

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| **LCP** (Largest Contentful Paint) | < 2.5s | Lighthouse, Vercel Analytics | 🔴 Critical |
| **FID** (First Input Delay) | < 100ms | CrUX, Lighthouse | 🔴 Critical |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Lighthouse | 🔴 Critical |
| **TTI** (Time to Interactive) | < 3.5s | Lighthouse | 🟡 High |
| **Bundle Size (Initial)** | < 150KB (gzip) | Webpack Bundle Analyzer | 🟡 High |
| **API Response Rendering** | < 200ms | Custom metrics | 🟡 High |
| **Form Rendering (100 fields)** | < 1s | Custom benchmark | 🟠 Medium |
| **Search/Filter Response** | < 500ms | Custom metrics | 🟠 Medium |

**Optimization Strategies:**
```typescript
// Code Splitting by Route
const Dashboard = lazy(() => import('./pages/Dashboard'));
const FormBuilder = lazy(() => import('./pages/FormBuilder'));

// Component Lazy Loading
const Charts = lazy(() => import('./components/Charts'));
const PdfViewer = lazy(() => import('./components/PdfViewer'));

// Image Optimization
import Image from 'next/image';
<Image src="/logo.png" width={200} height={50} priority />

// Font Optimization
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'], display: 'swap' });
```

---

### 5.2 Accessibility Requirements

**Standard:** WCAG 2.1 Level AA Compliance

#### 5.2.1 Keyboard Navigation
| Requirement | Implementation |
|-------------|----------------|
| All interactive elements | `tabindex` management, focus indicators |
| Keyboard shortcuts | `Ctrl+S` (Save), `Ctrl+P` (Preview), `Esc` (Close modal) |
| Skip links | Jump to main content, navigation |
| Focus traps | In modals, popovers, dialogs |
| Focus restoration | After closing modal, return focus |

**Implementation Example:**
```typescript
// Focus Trap in Modal
useEffect(() => {
  if (isOpen) {
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    firstElement?.focus();
    
    const handleTab = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };
    
    modal.addEventListener('keydown', handleTab);
    return () => modal.removeEventListener('keydown', handleTab);
  }
}, [isOpen]);
```

#### 5.2.2 Screen Reader Support
| Element | ARIA Attributes | Announcement |
|---------|-----------------|--------------|
| Form errors | `aria-live="polite"`, `aria-atomic="true"` | "Error: This field is required" |
| Loading states | `aria-busy="true"`, `aria-live="polite"` | "Loading..." |
| Toast notifications | `role="status"`, `aria-live="polite"` | Success/Error messages |
| Progress indicators | `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax` | "Upload progress: 50%" |
| Dynamic content | `aria-live="polite"` regions | Auto-announce changes |

#### 5.2.3 Color Contrast
```css
/* All text must meet WCAG AA (4.5:1 for normal, 3:1 for large) */
--text-primary: hsl(222.2 84% 4.9%); /* #000 on #FFF = 21:1 ✓ */
--text-secondary: hsl(215.4 16.3% 46.9%); /* Gray on white = 4.6:1 ✓ */
--error: hsl(0 84.2% 60.2%); /* Red on white = 4.5:1 ✓ */
--success: hsl(142.1 76.2% 36.3%); /* Green on white = 4.6:1 ✓ */
```

---

### 5.3 Browser Compatibility

| Browser | Minimum Version | Notes |
|---------|----------------|-------|
| Chrome | 90+ | Full support |
| Firefox | 88+ | Full support |
| Safari | 14+ | Full support |
| Edge | 90+ | Full support |
| Mobile Safari | iOS 14+ | Touch optimizations |
| Chrome Mobile | Android 8+ | PWA support |

**Polyfills Required:** None (Vite handles via browserslist)

---

### 5.4 PWA Requirements

#### 5.4.1 Manifest
```json
// public/manifest.json
{
  "name": "Form Management System",
  "short_name": "FormMS",
  "description": "Dynamic form builder and management",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0070f3",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["productivity", "business"],
  "screenshots": [...]
}
```

#### 5.4.2 Service Worker (Workbox)
```typescript
// Caching Strategy
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate, CacheFirst, NetworkFirst } from 'workbox-strategies';

// Static assets: Cache First
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'images' })
);

// API calls: Network First (offline fallback)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({ cacheName: 'api', networkTimeoutSeconds: 10 })
);

// HTML: Stale While Revalidate
registerRoute(
  ({ request }) => request.destination === 'document',
  new StaleWhileRevalidate({ cacheName: 'pages' })
);
```

#### 5.4.3 Background Sync (Offline Submissions)
```typescript
// Queue submissions when offline
import { Queue } from 'workbox-background-sync';

const queue = new Queue('form-submissions', {
  onSync: async ({ queue }) => {
    let entry;
    while ((entry = await queue.shiftRequest())) {
      try {
        await fetch(entry.request);
      } catch (error) {
        await queue.unshiftRequest(entry);
        throw error;
      }
    }
  }
});

// In submission handler
if (!navigator.onLine) {
  await queue.pushRequest({ request });
  toast.info('Submission queued. Will sync when online.');
} else {
  await fetch(request);
}
```

---

## 8. Security & Performance

### 8.1 Security Requirements

#### 8.1.1 XSS Protection
```typescript
// React auto-escapes by default, but for dynamic HTML:
import DOMPurify from 'dompurify';

const SafeHtml = ({ html }: { html: string }) => {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href']
  });
  
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
};
```

#### 8.1.2 CSRF Protection
```typescript
// SameSite cookies (backend sets this)
// For non-cookie auth, include CSRF token in headers
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
  headers: {
    'X-CSRF-Token': getCsrfToken() // From meta tag or cookie
  }
});
```

#### 8.1.3 Route Guards (Next.js Middleware)
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const { pathname } = request.nextUrl;
  
  // Public routes
  const publicRoutes = ['/login', '/register', '/submit'];
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }
  
  // Protected routes
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('from', pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
};
```

#### 8.1.4 Content Security Policy
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL};
    `.replace(/\s{2,}/g, ' ').trim()
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin'
  }
];

module.exports = {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  }
};
```

---

## 13. Error Handling Strategy

### 13.1 Error Categories

| Category | HTTP Status | User Action | System Action |
|----------|-------------|-------------|---------------|
| **Network** | N/A (offline) | "Check internet connection" | Retry with exponential backoff |
| **Validation** | 400, 422 | "Fix highlighted fields" | Show field-level errors |
| **Authentication** | 401 | "Please login again" | Redirect to login |
| **Authorization** | 403 | "You don't have permission" | Show error page |
| **Not Found** | 404 | "Resource not found" | Show 404 page |
| **Server Error** | 500 | "Something went wrong. Try again." | Log to Sentry, show generic error |
| **Rate Limit** | 429 | "Too many requests. Wait X seconds" | Show countdown timer |

### 13.2 Error Boundary Implementation

```typescript
// components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import * as Sentry from '@sentry/nextjs';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<FormBuilderErrorFallback />}>
  <FormBuilder />
</ErrorBoundary>
```

### 13.3 API Error Handler

```typescript
// lib/apiClient.ts
import axios, { AxiosError } from 'axios';
import { toast } from 'sonner';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true
});

// Response interceptor
api.interceptors.response.use(
  response => response,
  (error: AxiosError<ApiError>) => {
    const { response } = error;
    
    if (!response) {
      // Network error
      toast.error('Network error. Please check your connection.');
      return Promise.reject(error);
    }
    
    switch (response.status) {
      case 400:
      case 422:
        // Validation errors - handled by form
        break;
      
      case 401:
        // Unauthorized - redirect to login
        authStore.logout();
        window.location.href = '/login';
        break;
      
      case 403:
        toast.error('You don\'t have permission to perform this action');
        break;
      
      case 404:
        toast.error('Resource not found');
        break;
      
      case 429:
        const retryAfter = response.headers['retry-after'] || 60;
        toast.error(`Too many requests. Please wait ${retryAfter} seconds.`);
        break;
      
      case 500:
      case 502:
      case 503:
        toast.error('Server error. Please try again later.');
        // Log to error tracking
        logError(error);
        break;
      
      default:
        toast.error(response.data?.message || 'An error occurred');
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 13.4 Retry Logic

```typescript
// lib/retry.ts
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    delayMs?: number;
    backoff?: 'linear' | 'exponential';
  } = {}
): Promise<T> {
  const { maxAttempts = 3, delayMs = 1000, backoff = 'exponential' } = options;
  
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt < maxAttempts) {
        const delay = backoff === 'exponential'
          ? delayMs * Math.pow(2, attempt - 1)
          : delayMs * attempt;
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError!;
}

// Usage
const data = await withRetry(() => api.get('/api/v1/form/list'), {
  maxAttempts: 3,
  delayMs: 1000,
  backoff: 'exponential'
});
```

### 13.5 Offline Error Handling

```typescript
// hooks/useOnlineStatus.ts
import { useEffect, useState } from 'react';

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success('Connection restored');
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      toast.error('You are offline. Changes will be saved locally.');
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
}

// In form component
const isOnline = useOnlineStatus();

const handleSubmit = async (data) => {
  if (!isOnline) {
    // Queue for background sync
    await queueSubmission(formId, data);
    toast.info('Submission saved. Will sync when online.');
    return;
  }
  
  // Normal submission
  await api.post(`/api/v1/form/${formId}/responses`, { data });
};
```

---

## 14. Testing Requirements

### 14.1 Unit Testing

**Framework:** Vitest  
**Coverage Target:** 80% overall, 90% for critical paths

```typescript
// Example: Form validation test
import { describe, it, expect } from 'vitest';
import { generateFormSchema } from '@/lib/validation';

describe('Form Validation', () => {
  it('should require fields marked as required', () => {
    const form: IForm = {
      // ... form definition with required field
    };
    
    const schema = generateFormSchema(form);
    const result = schema.safeParse({ /* empty data */ });
    
    expect(result.success).toBe(false);
    expect(result.error?.issues[0].message).toBe('This field is required');
  });
  
  it('should validate email format', () => {
    const schema = z.string().email();
    
    expect(schema.safeParse('invalid').success).toBe(false);
    expect(schema.safeParse('valid@example.com').success).toBe(true);
  });
});
```

### 14.2 Component Testing

**Framework:** React Testing Library

```typescript
// Example: Button component test
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('should render children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('should call onClick handler', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('should be disabled when loading', () => {
    render(<Button loading>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### 14.3 Integration Testing

**Framework:** Playwright

```typescript
// tests/e2e/form-submission.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Form Submission Flow', () => {
  test('should submit a public form successfully', async ({ page }) => {
    // Navigate to form
    await page.goto('/submit/patient-registration');
    
    // Fill form
    await page.fill('[name="name"]', 'John Doe');
    await page.fill('[name="age"]', '35');
    await page.selectOption('[name="gender"]', 'Male');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Verify success
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page).toHaveURL(/.*\/success/);
  });
  
  test('should show validation errors', async ({ page }) => {
    await page.goto('/submit/patient-registration');
    
    // Submit without filling required fields
    await page.click('button[type="submit"]');
    
    // Verify errors
    await expect(page.locator('.error-message')).toContainText('This field is required');
  });
});
```

### 14.4 Accessibility Testing

```typescript
// tests/a11y/form-builder.spec.ts
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Form Builder Accessibility', () => {
  test('should have no accessibility violations', async ({ page }) => {
    await page.goto('/builder/new');
    await injectAxe(page);
    
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: {
        html: true
      }
    });
  });
  
  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/builder/new');
    
    // Tab through focusable elements
    await page.keyboard.press('Tab');
    let focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(['BUTTON', 'INPUT', 'A']).toContain(focused);
  });
});
```

### 14.5 Performance Testing

```typescript
// tests/performance/form-rendering.spec.ts
import { test, expect } from '@playwright/test';

test('should render large form within performance budget', async ({ page }) => {
  await page.goto('/submit/large-form-100-fields');
  
  const metrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      loadComplete: navigation.loadEventEnd - navigation.loadEventStart
    };
  });
  
  expect(metrics.domContentLoaded).toBeLessThan(1000); // < 1s
  expect(metrics.loadComplete).toBeLessThan(3000); // < 3s
});
```

---

**[Document Complete - See Appendices for additional details]**
