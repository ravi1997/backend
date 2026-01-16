# Snippet: Flutter pubspec.yaml

```yaml

name: my_app
description: A new Flutter project.
publish_to: 'none' # Remove this line if you wish to publish to pub.dev

version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  provider: ^6.0.0
  # flutter_riverpod: ^2.4.0
  
  # Navigation
  go_router: ^13.0.0
  
  # Networking
  http: ^1.1.0
  # dio: ^5.3.0

  # Storage
  shared_preferences: ^2.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true

  # assets:
  #   - assets/images/
```
