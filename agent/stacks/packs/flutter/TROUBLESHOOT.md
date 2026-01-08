# Flutter Troubleshooting

## Common Issues

### Gradle Build Fails
- **Symptom**: Android build errors.
- **Fix**: Check `android/build.gradle` Kotlin/AGP versions. Try `cd android && ./gradlew clean`.

### Pod Install Failed
- **Symptom**: iOS build errors.
- **Fix**: `cd ios && rm -rf Pods Podfile.lock && pod install --repo-update`.

### White Screen on Web
- **Symptom**: App loads but shows nothing.
- **Fix**: Check browser console for CanvasKit errors (CORS). Consider `flutter run -d chrome --web-renderer html` for debugging.

### Overflow Errors
- **Symptom**: Yellow/Black striped bars.
- **Fix**: Wrap widget in `Expanded`, `Flexible`, or `SingleChildScrollView`.
