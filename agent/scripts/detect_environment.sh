#!/bin/bash

# Detects the current environment mode for the AI Agent.
# Outputs: LOCAL_DEV, DOCKER_DEV, CI, or PROD_READONLY

# 1. CI Detection
if [ "$CI" = "true" ] || [ -n "$GITHUB_ACTIONS" ] || [ "$TRAVIS" = "true" ] || [ -n "$JENKINS_URL" ]; then
    echo "CI"
    exit 0
fi

# 2. Production Detection
# Check for explicit PROD flags or critical env vars
if [ "$NODE_ENV" = "production" ] || [ "$FLASK_ENV" = "production" ] || [ "$DJANGO_ENV" = "production" ]; then
    echo "PROD_READONLY"
    exit 0
fi

# Check for k8s service variables often present in pods
if [ -n "$KUBERNETES_PORT" ] && [ -z "$DEV_MODE" ]; then
     # Default to PROD in K8s unless explicitly overridden
    echo "PROD_READONLY"
    exit 0
fi

# 3. Docker Dev Detection
if [ -f "/.dockerenv" ] || [ "$DOCKER_CONTAINER" = "true" ]; then
    echo "DOCKER_DEV"
    exit 0
fi

# 4. Default to LOCAL_DEV
echo "LOCAL_DEV"
exit 0
