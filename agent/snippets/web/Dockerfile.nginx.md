# Snippet: Static Web (Nginx) Dockerfile

```dockerfile
# Scope: React, Vue, Vanilla JS/HTML
# Assumption: You have already built your app locally or in a previous step to 'dist/'

FROM nginx:1.25-alpine

# Copy static assets
# Adjust 'dist' to 'build' or 'out' depending on framework
COPY dist /usr/share/nginx/html

# (Optional) Custom Nginx Config
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```
