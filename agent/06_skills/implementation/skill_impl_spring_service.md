# Skill: Implement Spring Service

## Context

When adding business logic to a Java Spring Boot application.

## 1. Analysis

- **Interface**: Does it need an interface? (Best practice: Yes).
- **Injection**: What repositories or other services are needed?
- **Transactional**: Does it modify DB state?

## 2. Scaffold

```java
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class MyServiceImpl implements MyService {

    private final MyRepository repository;

    @Override
    @Transactional
    public void performAction(String data) {
        // Business logic
    }
}
```

## 3. Implementation Steps

1. Define Service Interface.
2. Create Implementation Class annotated with `@Service`.
3. Inject dependencies using Constructor Injection (Lombok `@RequiredArgsConstructor` or manual).
4. Implement methods.

## 4. Verification

- Unit test with JUnit + Mockito.
