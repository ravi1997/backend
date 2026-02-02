# Skill: Implement Flutter Widget

## Context

When building UI in Flutter.

## 1. Analysis

- **State**: Stateless or Stateful?
- **Responsiveness**: Needs `LayoutBuilder` or `MediaQuery`?
- **Theme**: Use `Theme.of(context)`.

## 2. Scaffold

```dart
import 'package:flutter/material.dart';

class MyWidget extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const MyWidget({
    Key? key, 
    required this.label, 
    required this.onTap
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16.0),
        color: Theme.of(context).primaryColor,
        child: Text(label),
      ),
    );
  }
}
```

## 3. Implementation Steps

1. Choose Widget type.
2. Define final fields and constructor.
3. Build the widget tree.
4. Style using Context Theme.

## 4. Verification

- Widget Test checks if it pumps and finds text.
