# Dev Environment for AI Agent MD Pack
# Includes tools for validation and maintenance (markdownlint, etc.)

FROM node:20-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache bash git

# Install global tools
RUN npm install -g markdownlint-cli

# Copy project
COPY . .

# Default command: Lint all markdown files
CMD ["markdownlint", "**/*.md"]
