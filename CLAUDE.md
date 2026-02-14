# CLAUDE.md — Meditation Companion

## Project Overview

Cross-platform meditation app built with **Flutter** (Dart SDK ^3.6.1) using the **BLoC pattern** for state management. Currently in MVP phase with authentication feature implemented using a mock repository. Production backend will use Supabase.

- **Package name**: `meditation_companion`
- **Version**: 1.0.0+1
- **Platforms**: Android, iOS, Web, macOS, Linux
- **Android Application ID**: `pashutin.igor.georgia.meditation_companion`

## Repository Structure

```
meditation_companion/
├── app/                          # Flutter application root
│   ├── lib/                      # Source code
│   │   ├── main.dart             # Entry point
│   │   └── features/             # Feature modules
│   │       └── auth/             # Authentication feature (MVP)
│   │           ├── bloc/         # AuthBloc, events, states
│   │           ├── models/       # UserModel
│   │           ├── repository/   # Abstract + mock repository
│   │           ├── exceptions/   # AuthException
│   │           └── views/        # AuthWrapper, LoginScreen
│   ├── test/                     # Test suite
│   │   ├── features/auth/bloc/   # BLoC unit tests
│   │   └── widget/               # Widget tests
│   ├── android/                  # Android platform config
│   ├── ios/                      # iOS platform config
│   ├── web/                      # Web platform config
│   ├── macos/                    # macOS platform config
│   ├── linux/                    # Linux platform config
│   ├── pubspec.yaml              # Dependencies
│   └── analysis_options.yaml     # Linting config (flutter_lints)
├── docs/                         # Project documentation
│   ├── code_conventions/         # Coding standards
│   │   ├── state_management.md   # BLoC pattern guidelines
│   │   ├── testing_strategy.md   # TDD strategy
│   │   └── new_feature_implementation.md
│   ├── mvp/                      # MVP feature specs
│   └── roadmap.md                # Development phases
├── .roo/rules-code/rules.md      # Development rules & templates
└── .vscode/launch.json           # Debug configurations
```

## Common Commands

All Flutter commands must be run from the `app/` directory:

```bash
cd app

# Run tests
flutter test

# Run a specific test file
flutter test test/features/auth/bloc/auth_bloc_test.dart

# Run static analysis / linting
flutter analyze

# Get dependencies
flutter pub get

# Run the app (various targets)
flutter run                  # Default connected device
flutter run -d chrome        # Web (Chrome)
flutter run --release        # Release mode
flutter run --profile        # Profile mode

# Build
flutter build apk            # Android
flutter build ios             # iOS
flutter build web             # Web
```

## Architecture & Conventions

### Feature Structure (Required)

Every feature must follow this directory layout:

```
features/<feature_name>/
├── bloc/
│   ├── <feature>_bloc.dart
│   ├── <feature>_event.dart
│   └── <feature>_state.dart
├── models/
│   └── <feature>_model.dart
├── repository/
│   ├── <feature>_repository.dart      # Abstract interface
│   └── mock_<feature>_repository.dart  # Mock implementation
├── exceptions/
│   └── <feature>_exception.dart
└── views/
    └── <feature>_view.dart
```

### State Management — BLoC Pattern

- Use `flutter_bloc` (^8.1.0) with `equatable` (^2.0.5) for all state management
- Events: noun + verb pattern (e.g., `SignInRequested`, `AuthCheckRequested`)
- States: noun + adjective pattern (e.g., `Authenticated`, `Unauthenticated`)
- Each BLoC has a single responsibility — no nested BLoCs
- No business logic in widgets; all logic lives in BLoCs
- No direct state manipulation — always dispatch events
- Refer to `docs/code_conventions/state_management.md` for detailed patterns

### Naming Conventions

| Element           | Convention    | Example                    |
|-------------------|---------------|----------------------------|
| Files             | snake_case    | `auth_bloc.dart`           |
| Classes           | PascalCase    | `AuthBloc`                 |
| Variables/methods | camelCase     | `signInWithEmail`          |
| Private members   | _camelCase    | `_authRepository`          |
| BLoC files        | feature_bloc  | `auth_bloc.dart`           |
| Test files        | feature_test  | `auth_bloc_test.dart`      |

### Code Organization Within Files

Maintain this ordering in each Dart file:

1. Imports (dart → package → relative)
2. Part declarations
3. Class documentation
4. Class declaration
5. Private variables
6. Public variables
7. Constructors
8. Public methods
9. Private methods

## Testing

### Test-Driven Development (TDD)

This project follows strict TDD. Implementation order for any feature:

1. Write unit tests (models, repositories)
2. Implement models and repositories
3. Write BLoC tests
4. Implement BLoC
5. Write widget tests
6. Implement UI

**Never skip writing tests.**

### Test Stack

- `flutter_test` — Flutter widget/unit testing
- `bloc_test` (^9.1.0) — BLoC-specific test utilities
- `mockito` (^5.4.4) — Mocking
- `test` (^1.24.9) — Pure Dart unit tests

### Test File Locations

```
app/test/
├── features/auth/bloc/
│   └── auth_bloc_test.dart          # BLoC unit tests (7 cases)
├── widget/
│   ├── auth_wrapper_test.dart       # Navigation widget tests
│   └── components/
│       └── login_screen_test.dart   # Form/UI widget tests
└── widget_test.dart                 # Default template test
```

### Verification Checklist

Before considering any feature complete:

- [ ] Unit tests exist for models
- [ ] BLoC tests cover all states and events
- [ ] Widget tests cover UI components
- [ ] All tests pass (`flutter test`)
- [ ] Static analysis passes (`flutter analyze`)
- [ ] File structure matches convention
- [ ] Naming follows conventions
- [ ] Public APIs are documented

## Dependencies

### Runtime

| Package          | Version | Purpose                |
|------------------|---------|------------------------|
| flutter          | SDK     | Core framework         |
| flutter_bloc     | ^8.1.0  | State management       |
| equatable        | ^2.0.5  | Value equality         |
| cupertino_icons  | ^1.0.8  | iOS-style icons        |

### Dev

| Package          | Version | Purpose                |
|------------------|---------|------------------------|
| flutter_test     | SDK     | Testing framework      |
| bloc_test        | ^9.1.0  | BLoC testing utilities |
| mockito          | ^5.4.4  | Mocking                |
| test             | ^1.24.9 | Dart unit tests        |
| flutter_lints    | ^5.0.0  | Linting rules          |

## Current State

- **Auth feature**: Implemented with MockAuthRepository (in-memory, no persistence)
- **Test user**: `test@example.com` / `password123` (mock repo only)
- **Mock delay**: 1000ms simulated network latency in MockAuthRepository
- **No CI/CD pipeline** configured yet
- **No persistent database** — planned Supabase integration
- **No .env files** — environment config not yet needed

## Key Documentation

Consult these files before modifying code in their respective areas:

- `docs/code_conventions/state_management.md` — BLoC patterns, event/state design
- `docs/code_conventions/testing_strategy.md` — TDD workflow, coverage goals
- `docs/code_conventions/new_feature_implementation.md` — Feature scaffolding process
- `docs/roadmap.md` — MVP phases and planned features
- `.roo/rules-code/rules.md` — Enforcement rules, templates, and anti-patterns
