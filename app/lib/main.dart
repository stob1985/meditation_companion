import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:meditation_companion/features/auth/bloc/auth_bloc.dart';
import 'package:meditation_companion/features/auth/bloc/auth_event.dart';
import 'package:meditation_companion/features/auth/bloc/auth_state.dart';
import 'package:meditation_companion/features/auth/repository/mock_auth_repository.dart';
import 'package:meditation_companion/features/auth/views/login_screen.dart';
import 'package:meditation_companion/features/astrokin/astrokin.dart';

void main() {
  runApp(const AstroKinApp());
}

class AstroKinApp extends StatelessWidget {
  const AstroKinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (context) => AuthBloc(
            authRepository: MockAuthRepository(),
          )..add(AuthCheckRequested()),
        ),
        BlocProvider(
          create: (context) => AstroKinBloc(
            repository: MockAstroKinRepository(),
          ),
        ),
      ],
      child: MaterialApp(
        title: 'AstroKin',
        debugShowCheckedModeBanner: false,
        theme: AstroKinTheme.lightTheme,
        darkTheme: AstroKinTheme.darkTheme,
        themeMode: ThemeMode.light,
        home: const AstroKinAuthWrapper(),
      ),
    );
  }
}

class AstroKinAuthWrapper extends StatelessWidget {
  const AstroKinAuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        // Show loading indicator while checking authentication
        if (state is AuthInitial) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        // Show home screen if authenticated
        if (state is Authenticated) {
          return const AstroKinAppShell();
        }

        // Show error state with retry option
        if (state is AuthError) {
          return Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 48,
                    color: Colors.red,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Authentication Error',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    state.message,
                    style: Theme.of(context).textTheme.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {
                      context.read<AuthBloc>().add(AuthCheckRequested());
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          );
        }

        // Show login screen if unauthenticated
        return const LoginScreen();
      },
    );
  }
}
