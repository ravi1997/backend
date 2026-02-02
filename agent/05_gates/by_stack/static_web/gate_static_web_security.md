# Gate: Static Web Security

**Stack**: Static Web  
**Type**: Security Validation  
**Purpose**: Ensure static web projects follow security best practices

---

## Checks

### 1. Content Security Policy (CSP)

- [ ] CSP meta tag or header configured
- [ ] No inline scripts (or nonce/hash used)
- [ ] No inline styles (or nonce/hash used)
- [ ] Restrict script sources to trusted domains
- [ ] Restrict style sources to trusted domains

**Example CSP**:

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' https://trusted-cdn.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;">
```

### 2. XSS Prevention

- [ ] No user input rendered without sanitization
- [ ] innerHTML usage reviewed and sanitized
- [ ] URL parameters validated before use
- [ ] No eval() or Function() constructor
- [ ] No document.write() with user input

**Tool**: Manual code review, `eslint-plugin-security`

### 3. Sensitive Data Exposure

- [ ] No API keys in JavaScript
- [ ] No credentials in code
- [ ] No sensitive data in localStorage/sessionStorage
- [ ] No PII in URLs or logs
- [ ] .env files not committed (if using build tools)

**Tool**: `git-secrets`, manual review

### 4. Third-Party Dependencies

- [ ] All CDN resources use SRI (Subresource Integrity)
- [ ] HTTPS used for all external resources
- [ ] Trusted CDNs only (cdnjs, unpkg, jsDelivr)
- [ ] Minimal third-party scripts
- [ ] No outdated libraries with known vulnerabilities

**Example SRI**:

```html
<script src="https://cdn.example.com/lib.js" 
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..." 
        crossorigin="anonymous"></script>
```

### 5. HTTPS & Transport Security

- [ ] Site served over HTTPS (production)
- [ ] No mixed content (HTTP resources on HTTPS page)
- [ ] HSTS header configured (server-side)
- [ ] Secure cookies (if using cookies)

**Server Configuration** (example for Nginx):

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 6. Clickjacking Protection

- [ ] X-Frame-Options header set (server-side)
- [ ] CSP frame-ancestors directive set

**Server Configuration**:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
```

### 7. Information Disclosure

- [ ] No sensitive comments in HTML/JS
- [ ] No debug code in production
- [ ] No verbose error messages
- [ ] No directory listing enabled (server-side)
- [ ] No .git or .env exposed

### 8. Form Security

- [ ] CSRF protection (if forms submit to backend)
- [ ] Input validation on client and server
- [ ] No autocomplete on sensitive fields
- [ ] Proper input types (email, tel, url)

**Example**:

```html
<input type="password" name="password" autocomplete="off">
```

---

## Security Headers Checklist

Required headers (configured on web server):

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## Commands

### Check for Secrets

```bash
git secrets --scan
```

### Lint for Security Issues

```bash
npx eslint "**/*.js" --plugin security
```

### Security Headers Test

```bash
curl -I https://your-site.com | grep -E "(Content-Security-Policy|X-Frame-Options|X-Content-Type-Options)"
```

### Check SRI

```bash
# Manually verify all <script> and <link> tags have integrity attribute
grep -r "src=\"http" *.html
```

---

## Common Vulnerabilities

### ❌ BAD: Inline script without CSP

```html
<script>
  var userId = getUrlParam('id'); // XSS risk
  document.getElementById('user').innerHTML = userId;
</script>
```

### ✅ GOOD: Sanitized and external script

```html
<script src="app.js"></script>
<!-- In app.js: -->
<!-- const userId = DOMPurify.sanitize(getUrlParam('id')); -->
<!-- document.getElementById('user').textContent = userId; -->
```

### ❌ BAD: No SRI on CDN resource

```html
<script src="https://cdn.example.com/jquery.min.js"></script>
```

### ✅ GOOD: SRI on CDN resource

```html
<script src="https://cdn.example.com/jquery.min.js" 
        integrity="sha384-..." 
        crossorigin="anonymous"></script>
```

### ❌ BAD: API key in JavaScript

```javascript
const API_KEY = 'sk_live_1234567890abcdef';
```

### ✅ GOOD: API key on server-side

```javascript
// Use server-side proxy to call API with key
fetch('/api/proxy', { method: 'POST', body: data });
```

---

## Pass Criteria

✅ **PASS** if:

- CSP configured
- No XSS vulnerabilities
- No secrets in code
- All CDN resources use SRI
- HTTPS enforced
- Security headers configured

❌ **FAIL** if:

- No CSP
- XSS vulnerabilities found
- Secrets in code
- Missing SRI on CDN resources
- HTTP used in production
- Critical security headers missing

---

## Exceptions

- **Development**: HTTP allowed in local development
- **Inline styles**: Allowed if CSP uses nonce/hash
- **Third-party widgets**: May require CSP exceptions (document why)

---

## Security Checklist

```markdown
## Static Web Security Checklist

### Content Security Policy
- [ ] CSP meta tag or header present
- [ ] No unsafe-inline for scripts (or nonce used)
- [ ] Script sources whitelisted

### XSS Prevention
- [ ] No innerHTML with user input
- [ ] No eval() or Function()
- [ ] URL parameters validated

### Secrets & Credentials
- [ ] No API keys in code
- [ ] No credentials in code
- [ ] .env not committed

### Third-Party Resources
- [ ] All CDN scripts have SRI
- [ ] HTTPS for all external resources
- [ ] Trusted CDNs only

### Transport Security
- [ ] HTTPS in production
- [ ] No mixed content
- [ ] HSTS header configured

### Headers
- [ ] X-Frame-Options set
- [ ] X-Content-Type-Options set
- [ ] Referrer-Policy set

### Code Review
- [ ] No sensitive comments
- [ ] No debug code
- [ ] No verbose errors
```

---

## Tools

- **eslint-plugin-security**: Detect security issues in JavaScript
- **git-secrets**: Prevent committing secrets
- **DOMPurify**: Sanitize HTML to prevent XSS
- **SecurityHeaders.com**: Test security headers
- **Mozilla Observatory**: Comprehensive security scan

---

## Related Files

- `gate_static_web.md` (master gate)
- `gate_static_web_build.md`
- `agent/10_security/security_checklist.md`
