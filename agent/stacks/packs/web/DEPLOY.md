# Web Deployment Guide

## Static Site (SPA)

React, Vue, Vite, etc.

1. **Build**: `npm run build`
2. **Output**: `dist/` or `build/`
3. **Serve**: Any static file server (Nginx, S3+CloudFront, Netlify, Vercel).

## Server-Side Rendered (SSR)

Next.js, Nuxt, Remix.

1. **Build**: `npm run build`
2. **Start**: `npm start`
3. **Environment**: Requires Node.js runtime.

## Docker Deployment

See `agent/snippets/Dockerfile.node.md`.

### Nginx Strategy (SPA)

**Ref**: `agent/snippets/web/Dockerfile.nginx.md`

```dockerfile
COPY --from=builder /app/dist /usr/share/nginx/html
```

### Node Strategy (SSR)

```dockerfile
CMD ["npm", "start"]
```
