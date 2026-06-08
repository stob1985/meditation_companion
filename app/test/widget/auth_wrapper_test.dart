import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:meditation_companion/features/auth/bloc/auth_bloc.dart';
import 'package:meditation_companion/features/auth/bloc/auth_state.dart';
import 'package:meditation_companion/features/auth/repository/mock_auth_repository.dart';
import 'package:meditation_companion/features/auth/views/auth_wrapper.dart';
import 'package:meditation_companion/features/auth/views/login_screen.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

void main() {
  group('AuthWrapper', () {
    late MockAuthRepository authRepository;
    late AuthBloc authBloc;

    setUp(() {
      authRepository = MockAuthRepository();
      authBloc = AuthBloc(authRepository: authRepository);
    });

    tearDown(() {
      authBloc.close();
    });

    testWidgets('shows LoginScreen when not authenticated', (tester) async {
      // Start with Unauthenticated state
      authBloc.emit(Unauthenticated());

      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider.value(
            value: authBloc,
            child: const AuthWrapper(),
          ),
        ),
      );

      // Wait for the widget to build
      await tester.pump();

      // Should show login screen
      expect(find.byType(LoginScreen), findsOneWidget);
    });

    testWidgets('shows loading indicator initially', (tester) async {
      // Start with initial state
      authBloc.emit(AuthInitial());

      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider.value(
            value: authBloc,
            child: const AuthWrapper(),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows error message on auth failure', (tester) async {
      // Start with error state
      const errorMessage = 'Authentication failed';
      authBloc.emit(const AuthError(message: errorMessage));

      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider.value(
            value: authBloc,
            child: const AuthWrapper(),
          ),
        ),
      );

      // Wait for the widget to build
      await tester.pump();

      // Error message and try again button should be visible
      expect(find.text(errorMessage), findsOneWidget);
      expect(find.text('Try Again'), findsOneWidget);
    });
  });
}
